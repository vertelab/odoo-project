from odoo import models, fields, api, _


class ITAssets(models.Model):
    _name = 'it.asset'
    _description = 'IT Asset'

    name = fields.Char(string="Name")
    asset_file = fields.Binary(string="File")
    asset_file_filename = fields.Char(string="File Name")
    purchase_date = fields.Date(string="Purchase Date")
    qty = fields.Integer(string="Quantity")
    total = fields.Float(string="Total")
    asset_id = fields.Many2one('account.asset', string="Asset")
    partner_id = fields.Many2one('res.partner', string="Store")
