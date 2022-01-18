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
    wcag_state_ids = fields.Many2many(comodel_name = "wcag.state", relation ="wcag_rule_wcag_state", string = "Wcag States", help = "The states which this rule belongs to")
    task_wcag_ids = fields.One2many(comodel_name='project.task.wcag', string="Wcags", help="Is a list of wcag criteria for this task/object", inverse_name='wcag_id') 
    
#Gonna be a subset of rules for a project
class WcagState(models.Model):
    _name = 'wcag.state'
    name = fields.Char()
    wcag_rule_ids = fields.Many2many(comodel_name = "wcag.rule", relation ="wcag_rule_wcag_state", string = "Wcag Rules", help = "The wcag rules we are measuring each object against")
    project_id = fields.Many2many(comodel_name = "project.project", relation ="wcag_state_project_project", string = "Project", inverse_name='wcag_state_ids')
    
    
class ProjectTaskWcag(models.Model):
    _name = 'project.task.wcag'
    wcag_id = fields.Many2one(comodel_name = "wcag.rule", string = "Wcag Rule")
    task_id = fields.Many2one(comodel_name = "project.task",string = "Project Task")
    wcag_state = fields.Selection([ ('not_reviewed', 'Not reviewed'),('done', 'Done'),('partially_ok', 'Partially Ok'),('not_approved ', 'Not approved'),('not_relevant', 'Not Relevant'),],'State', default='not_reviewed')



    
    
