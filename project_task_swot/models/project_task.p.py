# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = "project.task"

    number = fields.Char("Number", default=lambda self: _('New'),
                     copy=False, readonly=True, tracking=True)
    
    def _get_selection_options(self):
        # Compute your options here
        return [('x_low',self.x_low),('x_high',self.x_high),('y_low',self.y_low),('y_high',self.y_high)]
        
    quadrant = fields.Selection(selection=_get_selection_options, string='Quadrant')


   
