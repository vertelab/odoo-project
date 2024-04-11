from odoo import models, fields, api

class projectModuleMonitor(models.TransientModel):
    _inherit = 'project.project'
    
    @api.model
    def _get_odoo_version(self):
        is_odoo_version = fields.Boolean.(string="Is Odoo varsion")
