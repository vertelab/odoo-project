from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'

    is_wcag = fields.Boolean(default=False, string="Wcag Project")
    project_wcag_rule_ids = fields.One2many(comodel_name="wcag.project.rule",
                                            inverse_name='project_id',
                                            string="Wcag Project Rules",
                                            help="The wcag rules we are measuring each object against, "
                                                 "specific to each project")

    def add_project_task_wcag(self):
        _logger.warning("add_project_task_wcag"*100)
        for record in self:
            _logger.warning(f"{record=}")
            tasks = self.env['project.task'].search([('project_id','=',record.id)])
            _logger.warning(f"{tasks=}")
            for task in tasks:
                _logger.warning(f"{task=}")
                for project_rule in record.project_wcag_rule_ids:
                    _logger.warning(f"{project_rule=}")
                    if not self.env['project.task.wcag'].search([('wcag_id', '=', project_rule.wcag_id.id),
                                                                 ('task_id', '=', task.id)]):
                        self.env['project.task.wcag'].create({
                            'wcag_id': project_rule.wcag_id.id,
                            'wcag_project_id': project_rule.id,
                            'task_id': task.id})
                    
                
        
    def set_display_name_wcag_rules(self):
        for rule in self.project_wcag_rule_ids:
            rule.set_display_name()
