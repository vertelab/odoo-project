from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = "project.project"

    asset_ids = fields.One2many('account.asset', 'project_id', string="Assets")

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        for rec in self:
            rec.asset_count = len(self.asset_ids)

    asset_count = fields.Integer(string="Assets", compute=_compute_asset_count)

    def action_view_assets(self):
        return {
            'name': _('Project Assets'),
            'view_mode': 'tree,form',
            'res_model': 'account.asset',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id
            },
        }

    def action_create_asset(self):
        return {
            'name': _('Project Asset Wizard'),
            'view_mode': 'form',
            'res_model': 'project.asset.wizard',
            'type': 'ir.actions.act_window',
            'context': {
                'default_project_id': self.id
            },
            'target': 'new'
        }

