from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = "project.project"

    other_partner_ids = fields.Many2many('res.partner', string="Other Customers")
