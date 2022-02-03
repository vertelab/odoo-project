from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

#Gonna be a list of rules based on a excel spread sheet
class WcagRule(models.Model):
    _name = 'wcag.rule'
    _rec_name = 'wcag_name'
    # ~ wcag_name = fields.Char()
    wcag_name = fields.Char()
    w3c_no = fields.Char()
    description = fields.Char()
    project_ids = fields.Many2many(comodel_name = "project.project", relation ="wcag_rule_project", string = "Projects", help = "The projects which this rule belongs to")
    task_wcag_ids = fields.One2many(comodel_name='project.task.wcag', string="Wcags", help="Is a list of wcag criteria for this task/object", inverse_name='wcag_id') 
    
class ProjectTaskWcag(models.Model):
    _name = 'project.task.wcag'
    wcag_id = fields.Many2one(comodel_name = "wcag.rule", string = "Wcag Rule")
    task_id = fields.Many2one(comodel_name = "project.task",string = "Project Task")
    wcag_state = fields.Selection([ ('done', 'OK'), ('partially_ok', 'Partial'),('not_approved ', 'Failed'),('not_relevant', 'Not relevant'),('not_reviewed', '*blank*')],'State', default='not_relevant')
    notes = fields.Char(String = "Notes")


    
    
