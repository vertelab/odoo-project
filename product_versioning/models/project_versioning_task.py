from odoo import models, fields, api, _


class Task(models.Model):
    _name = "project.versioning.task"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _description = "Task Versioning"
    _order = "id desc"

    name = fields.Char(string='Title', track_visibility='always', required=True, index=True)

    create_date = fields.Datetime("Created On", readonly=True, index=True)
    write_date = fields.Datetime("Last Updated On", readonly=True, index=True)

    project_id = fields.Many2one('project.versioning.project', string='Project', index=True,
                                 track_visibility='onchange', change_default=True)
    notes = fields.Text(string='Notes')

    user_id = fields.Many2one('res.users',
                              string='Assigned to',
                              default=lambda self: self.env.uid,
                              index=True, track_visibility='always')
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True,
                                 related_sudo=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._get_main_company())
    parent_id = fields.Many2one('project.task', string='Parent Task', index=True)


