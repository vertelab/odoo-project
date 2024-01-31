from odoo import models, api, fields, _


class Project(models.Model):
    _inherit = 'project.project'

    store_id = fields.Many2one('res.partner', string="Store", domain="[('is_shop', '=', True)]")

    # domain="[('is_shop', '=', True)]"

    @api.depends('store_id')
    def _compute_store_asset(self):
        for rec in self:
            if rec.store_id:
                rec.asset_count = self.env['it.asset'].search_count([('partner_id', '=', rec.store_id.id)])
            else:
                rec.asset_count = 0

    asset_count = fields.Integer(string="Asset Count", compute=_compute_store_asset)

    def action_view_partner_assets(self):
        return {
            'name': _('Partner Assets'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.asset',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.store_id.id)]
        }


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # store_id = fields.Many2one('res.partner', string="Store")