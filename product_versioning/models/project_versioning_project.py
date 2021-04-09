from odoo import models, fields, api, _


class Project(models.Model):
    _name = "project.versioning.project"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _description = "Project Versioning"
    _order = "name, id"

    name = fields.Char("Version Name", index=True, required=True, track_visibility='onchange')
    project_id = fields.Many2one(comodel_name='project.project', string="Project")

    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    task_ids = fields.One2many('project.versioning.task', 'project_id', string='Tasks')
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
        
    def change_to_version(self, version):
        """
            1) if current version is latest, save current state "save_version()"
            2) copy choosen version to project.project / project.task  add button / wizard for version selection
            make sure that deleted and added tasks works
        """


