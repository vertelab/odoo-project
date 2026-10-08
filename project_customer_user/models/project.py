from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from odoo.osv import expression

CUSTOMER_GROUP = 'project_customer_user.group_project_customer_user'


# ----------------------------------------------------------------------
# The single authorisation predicate (design D5)
# ----------------------------------------------------------------------
#
# Module-level functions rather than model methods: both project.project and
# project.task need them, and an abstract mixin in _inherit collided with
# project.project's own fields (favorite_user_ids table reuse).
#
# Access is granted by `partner_id` or `customer_ids` — an explicit grant on
# the project.
#
# `message_partner_ids` is deliberately NOT part of this predicate. It is a
# mail-thread relation: "anyone who has ever been on the thread", including
# CCs, followers and mentioned colleagues. The module additionally subscribes
# partners as a side effect of write()/create(), so including it meant *being
# emailed granted access*. Closing the URL bypass while leaving that would have
# closed the front door and left the back door open.
#
# This is the single source of truth, used by:
#   - the ir.rule records in security/groups.xml
#   - _search() / check_access_rule() below (defence in depth)
#   - controllers/web.py _login_redirect()
#
# The three sites used to disagree (the redirect was narrower than the rules),
# which made the redirect fall through for customers reachable only via
# message_partner_ids.


def is_customer_user(env, user=None):
    """True when the given user (default: current) is a project customer."""
    user = user or env.user
    return user.has_group(CUSTOMER_GROUP)


def customer_project_domain(env, partner=None):
    """Domain restricting projects to those the given partner is granted.

    Returns an empty list for users without the customer group, so callers can
    treat "empty" as "no restriction".
    """
    partner = partner or env.user.partner_id
    return [
        '|',
        ('partner_id', '=', partner.id),
        ('customer_ids', 'in', [partner.id]),
    ]


def customer_task_domain(env, partner=None):
    """Domain restricting tasks to those the given partner is granted.

    A task is reachable when the task itself is granted (partner_id) or its
    project is granted (project_id.partner_id / project_id.customer_ids).
    """
    partner = partner or env.user.partner_id
    return [
        '|', '|',
        ('partner_id', '=', partner.id),
        ('project_id.customer_ids', 'in', [partner.id]),
        ('project_id.partner_id', '=', partner.id),
    ]


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Reverse relations used by the res.partner record rule in
    # security/groups.xml. Without a rule, perm_read=True on the ACL means
    # "read every partner" — which is how a customer could list all 3620
    # (verified 2026-10-03). The ACL grants the capability; the rule supplies
    # the boundary (design D1).
    customer_project_ids = fields.Many2many(
        comodel_name="project.project",
        relation="project_project_res_partner_rel",
        column1="res_partner_id",
        column2="project_project_id",
        string="Customer projects",
        compute="_compute_customer_project_ids",
    )
    customer_task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="partner_id",
        string="Customer tasks",
        compute="_compute_customer_task_ids",
    )

    def _compute_customer_project_ids(self):
        Project = self.env["project.project"].sudo()
        for partner in self:
            partner.customer_project_ids = Project.search(
                [
                    "|",
                    ("partner_id", "=", partner.id),
                    ("customer_ids", "in", [partner.id]),
                ]
            )

    def _compute_customer_task_ids(self):
        Task = self.env["project.task"].sudo()
        for partner in self:
            partner.customer_task_ids = Task.search(
                [("partner_id", "=", partner.id)]
            )


class ProjectProject(models.Model):
    _inherit = "project.project"

    customer_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Customers",
        help=(
            "Partners who may see this project and its tasks.\n"
            "\n"
            "Two things are needed for a customer to get access:\n"
            "  1. the partner's user must be in the 'Project Customer' group\n"
            "     (Settings > Users > Access Rights > Project), and\n"
            "  2. the partner must be listed here.\n"
            "\n"
            "This field grants the access; the group grants the rights. "
            "Adding a partner here without the group gives them nothing, "
            "and the group without this field gives them an empty project "
            "list."
        ),
    )

    @api.model
    def _is_customer_user(self, user=None):
        return is_customer_user(self.env, user)

    @api.model
    def _customer_project_domain(self, partner=None):
        return customer_project_domain(self.env, partner)

    def _get_customer_domain(self):
        """Customer restriction for the current user, or [] if not a customer."""
        if self._is_customer_user():
            return self._customer_project_domain()
        return []

    @api.model
    def _search(self, args, **kwargs):
        domain = self._get_customer_domain()
        if domain:
            args = expression.AND([args, domain]) if args else domain
        return super()._search(args, **kwargs)

    def check_access_rule(self, operation):
        super().check_access_rule(operation)
        domain = self._get_customer_domain()
        if domain:
            if operation == 'read' and not self.filtered_domain(domain):
                raise AccessError(_('You are not allowed to access this project.'))

    def write(self, vals):
        res = super().write(vals)
        if 'partner_id' in vals or 'customer_ids' in vals:
            partners = self.partner_id | self.customer_ids
            if partners:
                self._message_subscribe(partner_ids=partners.ids)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            partners = record.partner_id | record.customer_ids
            if partners:
                record._message_subscribe(partner_ids=partners.ids)
        return records


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def _is_customer_user(self, user=None):
        return is_customer_user(self.env, user)

    def _get_customer_task_domain(self):
        """Customer restriction for tasks, or [] if not a customer."""
        if not self._is_customer_user():
            return []
        return customer_task_domain(self.env)

    @api.model
    def _search(self, args, **kwargs):
        domain = self._get_customer_task_domain()
        if domain:
            args = expression.AND([args, domain]) if args else domain
        return super()._search(args, **kwargs)

    def check_access_rule(self, operation):
        super().check_access_rule(operation)
        domain = self._get_customer_task_domain()
        if domain:
            if operation == 'read' and not self.filtered_domain(domain):
                raise AccessError(_('You are not allowed to access this task.'))

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks:
            if task.project_id:
                partners = task.project_id.partner_id | task.project_id.customer_ids
                if partners:
                    task._message_subscribe(partner_ids=partners.ids)
        # A customer who creates a task must be able to read it back.
        #
        # Found by the operator, 2026-10-03: saving a new task as a Project
        # Customer failed with
        #
        #     Tyvärr, Test Kund (id=2347) har inte "läsa" tillgång till:
        #     - Aktivitet (project.task)
        #
        # The task WAS created; the read-back was denied. Odoo's own rule
        # "Project/Task: employees: follow required for followers" carries the
        # comment "to subscribe check access to the record, follower is not
        # enough at creation" and requires ('user_ids', 'in', user.id). A
        # customer-created task had user_ids empty, so the rule excluded it
        # from the creator's own view.
        #
        # Adding the creator as an assignee is also what a regular project user
        # gets, so this matches the "same rights as a regular project user"
        # requirement rather than widening it.
        for task in tasks:
            if task.create_uid.id in task.project_id.customer_ids.mapped(
                "user_ids"
            ).ids and task.create_uid not in task.user_ids:
                task.sudo().write({"user_ids": [(4, task.create_uid.id)]})
        return tasks
