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
<<<<<<< HEAD
<<<<<<< HEAD
        res = super().write(vals)
        for record in self:
            if record.number == _('New'):
                if not record.env.user._is_portal():
                    # ~ vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
                    record.number = self.env['ir.sequence'].next_by_code('project.task.number') or False
                else:
                    # ~ vals['number'] = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or _('New')
                    record.number = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or False
        return res
=======
        for record in self:
            if record.number == _('New'):
                if not self.env.user._is_portal():
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
                else:
                    vals['number'] = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or _('New')
=======
        if self.number == _('New'):
            if not self.env.user._is_portal():
                vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
            else:
                vals['number'] = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or _('New')
>>>>>>> cfe9d6ecf0e05b0201c29f70adfc93deaee77578
        return super().write(vals)
>>>>>>> 8f662a71620d8af53ca9da65fc2e93bdfb736eb2
