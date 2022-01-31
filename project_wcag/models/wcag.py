from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

#Gonna be a list of rules based on a excel arc
class WcagRule(models.Model):
    _name = 'wcag.rule'
    
    name = fields.Char()
    w3c_no = fields.Char()
    description = fields.Char()
    project_ids = fields.Many2many(comodel_name = "project.project", relation ="wcag_rule_project", string = "Projects", help = "The projects which this rule belongs to")
    task_wcag_ids = fields.One2many(comodel_name='project.task.wcag', string="Wcags", help="Is a list of wcag criteria for this task/object", inverse_name='wcag_id') 
    
class ProjectTaskWcag(models.Model):
    _name = 'project.task.wcag'
    wcag_id = fields.Many2one(comodel_name = "wcag.rule", string = "Wcag Rule")
    task_id = fields.Many2one(comodel_name = "project.task",string = "Project Task")
    wcag_state = fields.Selection([ ('not_reviewed', 'Not reviewed'),('done', 'Done'),('partially_ok', 'Partially Ok'),('not_approved ', 'Not approved'),('not_relevant', 'Not Relevant'),],'State', default='not_reviewed')
    notes = fields.Char(String = "Notes")


    
    
