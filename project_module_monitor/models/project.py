from odoo import models, fields, api

class projectModuleMonitor(models.Model):
    _inherit = 'project.project'
    
    is_module_monitor = fields.Boolean(string="Is module monitor")

    def action_show_add_repo(self):
        return self.env.ref('project_module_monitor.action_project_module_monitor_wizard_view').read()[0]

    def action_add_stakeholder(self):
        return self.env.ref('project_module_monitor.action_project_add_stakeholder_wizard_view').read()[0]

class projectStage(models.Model):
    _inherit = 'project.task.type'
    
    monitor_odoo_version = fields.Boolean(string="Monitor Odoo version", help="Monitor an Odoo version named like the stage. E.g. 16.0, 17.0")
    def _is_module_monitor(self):
        self.is_module_monitor = len(self.project_ids.filtered(lambda p: p.is_module_monitor == True)) > 0
    is_module_monitor = fields.Boolean(compute="_is_module_monitor")

# ~ Example on such a stage are 12.0,13.0,14.0 etc.
class projectTask(models.Model):
    _inherit = 'project.task'

    module_author = fields.Char(string="Author") # example vertel,oca
    git_repo = fields.Char(string="Git Repo", help="For example l10n_se") # example l10n_se
    git_module = fields.Char(string="Git Module", help="For example, l10n_se_extended") # l10n_se_extended
    odoo_version = fields.Char(string='Odoo Version')
    module_stakeholder_ids = fields.Many2many(comodel_name='res.partner',string='Stake Holder') # SKF, Dollar, SFM
    is_module_monitor = fields.Boolean(related="project_id.is_module_monitor")

    module_summary = fields.Char(string='Summary')
    module_category = fields.Char(string='Category') # Selection?
    module_website = fields.Char(string='Website')
    module_images  = fields.Char(string='Images', )
    module_license = fields.Char(string='Licence') # Selection
    module_maintainer = fields.Char(string='Maintainer',)
    module_depends = fields.Char(string='Depends')
    module_installable = fields.Boolean(string='Installable')
    module_application = fields.Boolean(string='Application')
    module_auto_install = fields.Boolean(string="Auto install")
    module_branches = fields.Char(string='Branches',)
    module_website_desc = fields.Html(string='Website Description',)
    module_version_ids = fields.Many2many(comodel_name='project.task.type',string='Odoo versions',help="")

    #--potential extra fields.
    # ~ many2many = fields('odoo.version')
