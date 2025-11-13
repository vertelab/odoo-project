from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_hr_manager_user_id = fields.Many2one(
        'res.users', related='project_id.hr_manager_user_id',
        string='Department Project Manager User')