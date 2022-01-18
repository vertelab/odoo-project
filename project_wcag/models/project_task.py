from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
    

class ProjectTask(models.Model):
    _inherit = 'project.task'
    task_wcag_ids = fields.One2many(comodel_name='project.task.wcag', string="Wcags", help="Is a list of wcag criteria for this task/object", inverse_name='task_id' ) 
    
    rule_count = fields.Integer(compute='_compute_rule_count', string="Task Count")
    def _compute_rule_count(self):
        self.rule_count = len(self.task_wcag_ids) or 0

