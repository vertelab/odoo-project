from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    @api.model
    def _get_odoo_version(self):
        is_odoo_version = fields.Boolean.
