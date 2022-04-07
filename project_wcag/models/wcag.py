from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

ZERO_WIDTH_CHAR = '\u200b'

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
    # ~ wcag_state = fields.Selection([ ('done', 'OK'), ('partially_ok', 'Partial'),('not_approved', 'Failed'),('not_relevant', 'Not relevant'),('not_reviewed', '*blank*')],'State', default='not_relevant', group_operator="min")
    wcag_state = fields.Selection([('1', 'Failed'),('2', '*blank*'),('3', 'Not relevant'), ('4', 'Partial'), ('5', 'OK')],'State', default='3', group_operator="max")
    notes = fields.Text(String = "Notes", group_operator="max")
    # ~ user_id = fields.Many2one(comodel_name = "res.user")



    def get_project_id(self):
        if self.task_id:
            return self.task_id.project_id
        else:
            return False
        
    # ~ @api.depends('task_id')
    # ~ def compute_project_id(self):
        # ~ for task_wcag in self:
            # ~ task_wcag.task_project_id = task_wcag.task_id.project_id
    
    task_project_id = fields.Many2one(comodel_name="project.project", default=get_project_id, readonly=True)
    
    @api.model
    def create(self, vals):
        if vals['task_id']:
            vals['task_project_id'] = self.env['project.task'].browse(vals['task_id']).project_id.id
        else:
            vals['task_project_id'] = False
        res = super(ProjectTaskWcag, self).create(vals)
        # ~ if res.self.task_id:
            # ~ res.task_project_id = res.task_id.project_id
        return res
        
    def write(self, values):
        if 'task_id' in values:
            if values['task_id']:
                values['task_project_id'] = self.env['project.task'].browse(values['task_id']).project_id
            else:
                values['task_project_id'] = False
        res = super(ProjectTaskWcag, self).write(values)
        return res
        
   
    def action_read_task_rule(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task.wcag',
            'res_id': self.id,
        }
