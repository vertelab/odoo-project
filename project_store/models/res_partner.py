from odoo import models, api, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    is_shop = fields.Boolean(string="Is Shop")

