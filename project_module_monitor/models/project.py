from odoo import models, fields, api

class projectModuleMonitor(models.Model):
    _inherit = 'project.project'
    
    is_module_monitor = fields.Boolean(string="Is module monitor")
