from odoo import models, fields, api, _
import uuid


class Project(models.Model):
    _name = "project.versioning.project"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _description = "Project Versioning"
    _order = "name, id"

    name = fields.Char("Version Name", index=True, required=True, track_visibility='onchange')
    date_created = fields.Datetime(string="Versioning Date", default=lambda self: fields.Datetime.now())

    project_id = fields.Many2one(comodel_name='project.project', string="Project")
    project_name = fields.Char(string="Project Name")
    label_tasks = fields.Char(string="Task Name")

    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    @api.depends('project_id')
    def _get_project_task(self):
        for rec in self:
            if rec.project_id:
                versioning_task_ids = rec.env['project.versioning.task'].search([('project_id', '=', rec.project_id.id)])
                if versioning_task_ids:
                    rec.task_ids = [(4, versioning_task.id) for versioning_task in versioning_task_ids]
                else:
                    rec.task_ids = False
            else:
                rec.task_ids = False

    task_ids = fields.One2many('project.versioning.task', 'project_version_id', string='Tasks')
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user,
                              track_visibility="onchange")

    privacy_visibility = fields.Selection([
            ('followers', 'On invitation only'),
            ('employees', 'Visible by all employees'),
            ('portal', 'Visible by following customers'),
        ],
        string='Privacy', required=True,
        default='portal',
        help="Holds visibility of the tasks or issues that belong to the current project:\n"
                "- On invitation only: Employees may only see the followed project, tasks or issues\n"
                "- Visible by all employees: Employees may see all project, tasks or issues\n"
                "- Visible by following customers: employees see everything;\n"
                "   if website is activated, portal users may see project, tasks or issues followed by\n"
                "   them or by someone of their company\n")
    date = fields.Date(string='Creation Date', index=True, track_visibility='onchange')
    subtask_project_id = fields.Many2one('project.versioning.project', string='Sub-task Project', ondelete="restrict",
                                         help="Choosing a sub-tasks project will both enable sub-tasks and set their "
                                              "default project (possibly the project itself)")
    # task_ids

    def new_version(self):
        """
            Create new version of a project: create project_versioning.project - copy current values of all fields to project_versioing.project, 
            store new version id in name
            use sequence for numbering, a new sequence for each project, name prefix with project name [project]01
            
            create project_versioning.task for each task
            
            add button for this "New version"
            
        """
        
    def save_version(self):
        """
            Save changes from project to current version, add button for this "Save version"
            If not current/latest version create new version
            
            make sure that deleted and added tasks 
        """
        
    def change_to_version(self):
        """
            1) if current version is latest, save current state "save_version()"
            2) copy choosen version to project.project / project.task  add button / wizard for version selection
            make sure that deleted and added tasks works
        """
        project_id = self.env['project.project'].search([('id', '=', self.project_id.id)])
        filter_tasks = project_id.task_ids - self.task_ids.mapped('task_id')
        if filter_tasks:
            for _rec in filter_tasks:
                _rec.active = False

        project_id.write({
            'name': self.project_name,
            'user_id': self.user_id.id,
            'partner_id': self.partner_id.id,
            'privacy_visibility': self.privacy_visibility,
            'version_id': self.id,
            'label_tasks': self.label_tasks,
            'task_ids': [(1, task.task_id.id, {
                'name': task.task_name,
                'date_deadline': task.date_deadline,
                'date_last_stage_update': task.date_last_stage_update,
                'parent_id': task.parent_id.id,
                'priority': task.priority,
                'sequence': task.sequence,
                'tag_ids': task.tag_ids.ids,
                'kanban_state': task.kanban_state,
                'color': task.color,
                'user_email': task.user_email,
                'subtask_project_id': task.subtask_project_id.id,
                'email_from': task.email_from,
                'email_cc': task.email_cc,
                'description': task.description,
                'project_id': task.project_id.id,
                'active': True
            }) for task in self.task_ids]
        })
