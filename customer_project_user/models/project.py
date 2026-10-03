from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from odoo.osv import expression

CUSTOMER_GROUP = 'customer_project_user.group_project_customer_user'


class ProjectProject(models.Model):
    _inherit = "project.project"

    customer_ids = fields.Many2many(comodel_name="res.partner", string="Customers")

    # ------------------------------------------------------------------
    # The single authorisation predicate (design D5)
    # ------------------------------------------------------------------
    #
    # Access is granted by `partner_id` or `customer_ids` — an explicit grant
    # on the project.
    #
    # `message_partner_ids` is deliberately NOT part of this predicate. It is a
    # mail-thread relation: "anyone who has ever been on the thread", including
    # CCs, followers and mentioned colleagues. The module additionally
    # subscribes partners as a side effect of write()/create() below, so
    # including it meant *being emailed granted access*. Closing the URL bypass
    # while leaving that would have closed the front door and left the back
    # door open.
    #
    # This method is the single source of truth. It is used by:
    #   - the ir.rule records in security/groups.xml
    #   - _search() / check_access_rule() below (defence in depth)
    #   - controllers/web.py _login_redirect()
    #
    # The three sites used to disagree (the redirect was narrower than the
    # rules), which made the redirect fall through for customers reachable only
    # via message_partner_ids.

    @api.model
    def _customer_project_domain(self, partner=None):
        """Domain restricting projects to those the given partner is granted.

        Returns an empty list for users without the customer group, so callers
        can treat "empty" as "no restriction".
        """
        partner = partner or self.env.user.partner_id
        return [
            '|',
            ('partner_id', '=', partner.id),
            ('customer_ids', 'in', [partner.id]),
        ]

    @api.model
    def _is_customer_user(self, user=None):
        """True when the given user (default: current) is a project customer."""
        user = user or self.env.user
        return user.has_group(CUSTOMER_GROUP)

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

    def _get_customer_task_domain(self):
        """Customer restriction for tasks, or [] if not a customer.

        Mirrors ProjectProject._get_customer_domain(): a task is reachable when
        the task itself is granted (partner_id) or its project is granted
        (project_id.partner_id / project_id.customer_ids).
        """
        if not self._is_customer_user():
            return []
        partner = self.env.user.partner_id
        return [
            '|', '|',
            ('partner_id', '=', partner.id),
            ('project_id.customer_ids', 'in', [partner.id]),
            ('project_id.partner_id', '=', partner.id),
        ]

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
        return tasks
