from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    @api.model
    def _get_selection_options(self):
        # Define the selection options dynamically
        return [('1', 'Default'), ('2', 'Last')]

    my_field = fields.Selection(selection=_get_selection_options, config_parameter='task.order', required=True, default='1')