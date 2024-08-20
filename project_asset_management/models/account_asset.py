from odoo import models, fields, api, _


class AccountAsset(models.Model):
    _inherit = "account.asset"

    project_id = fields.Many2one('project.project', string="Project")
