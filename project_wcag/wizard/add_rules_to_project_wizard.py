# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2017 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning
import zipfile
import base64
import tempfile
from io import BytesIO
import csv

import logging
_logger = logging.getLogger(__name__)


class AddWcagRules(models.TransientModel):
    _name = 'add.wcag.rule.wizard'
    _description = 'Wcag Rule Import Wizard'
    wcag_rules = fields.Many2many('wcag.rule', required=False, string="'Wcag Rules'")
    
    def add_rules(self):
        for form in self:
            for active_id in self.env.context.get('active_ids', []):
                project_id = self.env['project.project'].browse(active_id)
                _logger.warning(f"project name: {project_id.name} {project_id=}")
                #Lägg till regler i 
                #vals = 
                for rule in self.wcag_rules:
                   self.env['wcag.project.rule'].create({'project_id':project_id.id,'wcag_id':rule.id})
                   #val=
                   

        return {'type': 'ir.actions.act_window_close'}
