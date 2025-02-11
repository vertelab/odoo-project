# -*- coding: utf-8 -*-


from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = "project.task"

    number = fields.Char("Number", default=lambda self: _('New'),
                     copy=False, readonly=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number', _('New')) == _('New'):
                vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if 'number' not in vals:
            for record in self:
                if record.number == _('New'):
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
        return super().write(vals)
