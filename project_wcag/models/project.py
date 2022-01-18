from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class Project(models.Model):
    _inherit = 'project.project'
    is_wcag = fields.Boolean(default=False)
    wcag_state_ids = fields.Many2many(comodel_name='wcag.state', string="Wcags", help="Is a list of wcag rules for tasks in this project") 
    # ~ @api.models
    # ~ def add_wcag_task_based_on_state(self):
        # ~ for task in project_tasks:

    def add_project_task_wcag(self):
        for record in self:
            tasks = self.env['project.task'].search([('project_id','=',record.id)])
            for task in tasks:
                for state in record.wcag_state_ids:
                    for rule in state.wcag_rule_ids:
                        if not self.env['project.task.wcag'].search([('wcag_id','=',rule.id),('task_id','=',task.id)]):
                            self.env['project.task.wcag'].create({'wcag_id':rule.id,'task_id':task.id})
                    
                
