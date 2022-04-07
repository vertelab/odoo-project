from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'
    is_wcag = fields.Boolean(default=False, string="Wcag Project")
    wcag_rule_ids = fields.Many2many(comodel_name = "wcag.rule", relation ="wcag_rule_project", string = "Wcag Rules", help = "The wcag rules we are measuring each object against")
# ~ @api.models
    # ~ def add_wcag_task_based_on_state(self):
        # ~ for task in project_tasks:

    def add_project_task_wcag(self):
        _logger.warning("add_project_task_wcag"*100)
        for record in self:
            tasks = self.env['project.task'].search([('project_id','=',record.id)])
            for task in tasks:
               for rule in record.wcag_rule_ids:
                   if not self.env['project.task.wcag'].search([('wcag_id','=',rule.id),('task_id','=',task.id)]):
                       self.env['project.task.wcag'].create({'wcag_id':rule.id,'task_id':task.id})
                    
                
