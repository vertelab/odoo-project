from odoo import models, api, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    it_asset_ids = fields.One2many('it.asset', 'partner_id', string="IT Assets")

