from odoo import models, fields, api, _


class ITAssets(models.Model):
    _name = 'it.asset'
    _description = 'IT Asset'

    name = fields.Char(string="Name")
    fil = fields.Boolean(string="FIL", default=False)
    purchase_date = fields.Date(string="Purchase Date")
    created_by = fields.Many2one('res.users', string="Created By")
    number = fields.Integer(string="Total")
    total = fields.Float(string="Total")
    asset_id = fields.Many2one('account.asset', string="Asset")
