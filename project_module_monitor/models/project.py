from odoo import models, fields, api

class projectModuleMonitor(models.Model):
    _inherit = 'project.project'
    
    is_module_monitor = fields.Boolean(string="Is module monitor")

class projectStage(models.Model):
    _inherit = 'project.task.type'
    
    monitor_odoo_version = fields.Boolean(string="Monitor Odoo version", help="Monitor an Odoo version named like the stage. E.g. 16.0, 17.0")
    def _is_module_monitor(self):
        self.is_module_monitor = len(self.project_ids.filtered(lambda p: p.is_module_monitor == True)) > 0
    is_module_monitor = fields.Boolean(compute="_is_module_monitor")

# ~ Example on such a stage are 12.0,13.0,14.0 etc.
class projectTask(models.Model):
    _inherit = 'project.task'

    module_author = fields.Char(string="Authour") # example vertel,oca
    git_repo = fields.Char(string="Git Repo", help="For example l10n_se") # example l10n_se
    git_module = fields.Char(string="Git Module", help="For example, l10n_se_extended") # l10n_se_extended
    module_stakeholder_ids = fields.Many2many(comodel_name='res.partner',string='Stake Holder')
    is_module_monitor = fields.Boolean(related="project_id.is_module_monitor")

    #--potential extra fields.
    # ~ many2many = fields('odoo.version')
