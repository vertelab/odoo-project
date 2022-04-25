from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
    

class ProjectTask(models.Model):
    _inherit = 'project.task'
    team_id = fields.Many2one('crm.team', "Project Team", domain=[('type_team', '=', 'project')], readonly=True)

    @api.model
    def create(self, vals):
        #Get default values from selected wcag.rule
        if vals.get('project_id'):
            vals['team_id'] = self.env['project.project'].browse(vals['project_id']).team_id.id
        res = super(ProjectTask, self).create(vals)

        return res
