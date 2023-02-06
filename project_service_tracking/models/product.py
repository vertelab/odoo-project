from odoo import models, api, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_tracking = fields.Selection(selection_add=[
        ('tasks_target_project', 'Create tasks in an existing project')], default=None)

    target_project_id = fields.Many2one(
        'project.project', 'Target Project', company_dependent=True, copy=True,
        domain="[('company_id', '=', current_company_id)]",
        help='Select a billable project to be the skeleton of the new created project when selling the current product.'
             ' Its stages and tasks will be duplicated.')

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        if self.service_tracking == 'no':
            self.project_id = False
            self.project_template_id = False
        elif self.service_tracking == 'task_global_project':
            self.project_template_id = False
        elif self.service_tracking in ['task_in_project', 'project_only']:
            self.project_id = False
        elif self.service_tracking in ['tasks_target_project', 'project_only']:
            self.project_id = False
        elif self.service_tracking == 'tasks_target_project':
            self.project_template_id = False
            self.target_project_id = False
