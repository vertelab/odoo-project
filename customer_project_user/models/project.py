from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from odoo.osv import expression


class ProjectProject(models.Model):
    _inherit = "project.project"

    customer_ids = fields.Many2many(comodel_name="res.partner", string="Customers")

    def _get_customer_domain(self):
        if self.env.user.has_group('customer_project_user.group_project_customer_user'):
            return ['|', '|',
                ('partner_id', '=', self.env.user.partner_id.id),
                ('customer_ids', 'in', [self.env.user.partner_id.id]),
                ('message_partner_ids', 'in', [self.env.user.partner_id.id])]
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
        if self.env.user.has_group('customer_project_user.group_project_customer_user'):
            return ['|', '|',
                ('partner_id', '=', self.env.user.partner_id.id),
                ('project_id.customer_ids', 'in', [self.env.user.partner_id.id]),
                ('project_id.partner_id', '=', self.env.user.partner_id.id)]
        return []

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
