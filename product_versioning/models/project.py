from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    allow_versioning = fields.Boolean(string="Allow Versioning")
    versions = fields.Many2one('project.versioning.project', string="Project Versions")

    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        if res and self.allow_versioning:
            self.env['project.versioning.project'].create({
                'name': self.name,
                'project_id': self.id
                'user_id': self.user_id.id,
                'partner_id': self.partner_id.id,
                'privacy_visibility': self.privacy_visibility
            })
        return res
