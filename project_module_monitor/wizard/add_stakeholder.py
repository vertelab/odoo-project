from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import requests
import re


_logger = logging.getLogger(__name__)

class add_stakeholder(models.TransientModel):
    _name = "project.add.stakeholder.wizard"
    _description = "Add stakeholders to Projects."

    partner_id = fields.Many2one('res.partner')# example SKF, Skogsstyrelsen, Dollarstore
    stakeholder_file = fields.Binary(string='Stakeholder modules', help='Excel file exported from an Odoo instance.')
    
    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))

    def load_file(self):
        pass
        
        # ~ raise UserWarning("%s" % branches)
        # ~ https://raw.githubusercontent.com/vertelab/odoo-l10n_se/14.0/l10n_se_nordea/__manifest__.py
