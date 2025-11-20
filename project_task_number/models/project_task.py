# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)

PROJECT_TASK_FIELDS = {
    'number'
}

class Task(models.Model):
    _name = "project.task"
    _inherit = "project.task"

    number = fields.Char("Number", default=lambda self: _('New'),
                     copy=False, readonly=True, tracking=True)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | PROJECT_TASK_FIELDS

    @property
    def SELF_WRITABLE_FIELDS(self):
        return super().SELF_WRITABLE_FIELDS | PROJECT_TASK_FIELDS


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number', _('New')) == _('New'):
                if not self.env.user._is_portal():
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
                else:
                    vals['number'] = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if not vals:
            return True
        for record in self:
            if record.number == _('New'):
                if not self.env.user._is_portal():
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
                else:
                    vals['number'] = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or _('New')
        return super().write(vals)
