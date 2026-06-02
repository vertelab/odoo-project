from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    customer_ids = fields.Many2many(comodel_name="res.partner", string="Customers")

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

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks:
            if task.project_id:
                partners = task.project_id.partner_id | task.project_id.customer_ids
                if partners:
                    task._message_subscribe(partner_ids=partners.ids)
        return tasks
