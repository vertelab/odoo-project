from odoo import models, api, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    it_asset_id = fields.Many2one('it.asset', string="IT Asset")

