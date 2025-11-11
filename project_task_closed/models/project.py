import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('stage_id')
    def _compute_is_closed(self):
        for task in self:
            task.is_closed = task.stage_id.is_closed

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_closed = fields.Boolean(string="Closed")