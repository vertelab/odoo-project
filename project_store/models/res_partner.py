from odoo import models, api, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    is_shop = fields.Boolean(string="Is Shop")

    store_entrance_date = fields.Datetime(string="Store Entrance Date")
    store_opening_date = fields.Datetime(string="Store Opening Date")
    field_store_construction_day = fields.Date(string="Store Construction Day")
    store_day_one_new_ma = fields.Date(string="Store New MA")
    contractor_contract = fields.Many2one('res.partner', string="Contractor Contract")
    contact_person_establishment = fields.Many2one('res.partner', string="Contact Person Establishment")
    contact_person_sc = fields.Many2one('res.partner', string="Contact Person SC")
    contact_person_2 = fields.Many2one('res.partner', string="Contact Person 2")


