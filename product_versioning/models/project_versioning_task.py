from odoo import models, fields, api, _


class Task(models.Model):
    _name = "project.versioning.task"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _description = "Task Versioning"
    _order = "id desc"

    name = fields.Char("Version Name", index=True, required=True, track_visibility='onchange')
    date_created = fields.Datetime(string="Versioning Date", default=lambda self: fields.Datetime.now())
    project_version_id = fields.Many2one('project.versioning.project', string='Project Versioning', index=True,
                                         track_visibility='onchange', change_default=True)

    project_id = fields.Many2one(comodel_name='project.project', string="Project", track_visibility='always',
                                 required=True, index=True)
    task_id = fields.Many2one(comodel_name='project.task', string="Task", track_visibility='always', required=True,
                              index=True)
    task_name = fields.Char(string="Task Name", track_visibility='always', required=True, index=True)
    create_date = fields.Datetime("Created On", readonly=True, index=True)
    write_date = fields.Datetime("Last Updated On", readonly=True, index=True)
    date_start = fields.Datetime(string='Starting Date', default=fields.Datetime.now, index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, track_visibility='onchange')
    date_last_stage_update = fields.Datetime(string='Last Stage Update', index=True, copy=False, readonly=True)
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users',
                              string='Assigned to',
                              default=lambda self: self.env.uid,
                              index=True, track_visibility='always')
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True,
                                 related_sudo=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._get_main_company())
    partner_id = fields.Many2one('res.partner',
                                 string='Customer')
    parent_id = fields.Many2one('project.task', string='Parent Task', index=True)
    description = fields.Html(string='Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
    ], default='0', index=True, string="Priority")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
                              help="Gives the sequence order when displaying a list of tasks.")
    stage_id = fields.Many2one('project.task.type', string='Stage', ondelete='restrict', track_visibility='onchange')
    tag_ids = fields.Many2many('project.tags', string='Tags', oldname='categ_ids')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    color = fields.Integer(string='Color Index')
    user_email = fields.Char(related='user_id.email', string='User Email', readonly=True, related_sudo=False)
    subtask_project_id = fields.Many2one('project.project', related="project_id.subtask_project_id",
                                         string='Sub-task Project', readonly=True)
    email_from = fields.Char(string='Email', help="These people will receive email.", index=True)
    email_cc = fields.Char(string='Watchers Emails', help="""These email addresses will be added to the CC field of all inbound
            and outbound emails for this record before being sent. Separate multiple email addresses with a comma""")
    #
    # def change_to_version(self):
    #     task_id = self.env['project.task'].search([('id', '=', self.task_id.id)])
    #     task_id.write({
    #         'name': self.task_name,
    #         'user_id': self.user_id.id,
    #         'partner_id': self.partner_id.id,
    #         'date_assign': self.date_assign,
    #         'date_last_stage_update': self.date_last_stage_update,
    #         'sequence': self.sequence,
    #         'kanban_state': self.kanban_state,
    #         'priority': self.priority,
    #         'stage_id': self.stage_id.id,
    #         'description': self.description,
    #         'version_id': self.id
    #     })
    #
    #
