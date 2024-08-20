from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = "project.project"

    @api.depends('parent_id.ancestor_id')
    def _compute_ancestor_id(self):
        for project in self:
            project.ancestor_id = project.parent_id.ancestor_id or project.parent_id

    parent_id = fields.Many2one('project.project', string='Parent Project', index=True,
                                domain="['!', ('id', 'child_of', id)]", tracking=True)
    ancestor_id = fields.Many2one('project.project', string='Ancestor Project', compute='_compute_ancestor_id',
                                  index='btree_not_null', recursive=True, store=True)
    child_ids = fields.One2many('project.project', 'parent_id', string="Sub-Projects")

    @api.depends("child_ids")
    def _compute_project_count(self):
        for rec in self:
            rec.sub_project_count = len(self.child_ids)

    sub_project_count = fields.Integer(string="Sub-Projects", compute=_compute_project_count)

    def action_view_sub_projects(self):
        return {
            'name': _('Sub-Projects'),
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id
            },
        }
