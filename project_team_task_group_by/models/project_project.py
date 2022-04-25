from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
    

class ProjectTask(models.Model):
    _inherit = 'project.project'


    def write(self, values):
        if values.get('team_id'):
            for task in self.task_ids:
                task.team_id = values.get('team_id')
            

        res = super(ProjectTask, self).write(values)
        return res


