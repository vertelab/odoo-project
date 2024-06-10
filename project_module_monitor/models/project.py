from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ProjectModuleMonitor(models.Model):
    _inherit = 'project.project'

    is_module_monitor = fields.Boolean(string="Is module monitor")

    def action_show_add_repo(self):
        return self.env.ref('project_module_monitor.action_project_module_monitor_wizard_view').read()[0]

    def action_add_stakeholder(self):
        return self.env.ref('project_module_monitor.action_project_add_stakeholder_wizard_view').read()[0]

    def cron_monitor_module_version(self):
        for project in self.env['project.project'].search([('is_module_monitor', '=', True)]):
            for task in project.task_ids:
                _logger.warning(f"{task.name=}")
                if task.module_version_ids and task.git_owner and task.git_repo:
                    branch = task.project_id._get_latest_branch(
                        task.git_module,
                        git_owner=task.git_owner,
                        git_repo=task.git_repo
                    )
                    if task.odoo_version != branch:
                        version_id = self.env['project.task.type'].search(
                            [('project_ids', 'in', project.id), ('name', '=', branch)]
                        )
                        task.stage_id = version_id.id
                        task.odoo_version = branch


class ProjectStage(models.Model):
    _inherit = 'project.task.type'

    monitor_odoo_version = fields.Boolean(string="Monitor Odoo version",
                                          help="Monitor an Odoo version named like the stage. E.g. 16.0, 17.0")

    def _is_module_monitor(self):
        self.is_module_monitor = len(self.project_ids.filtered(lambda p: p.is_module_monitor)) > 0

    is_module_monitor = fields.Boolean(compute="_is_module_monitor")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    module_stakeholder_ids = fields.Many2many(comodel_name='res.partner', string='Stake Holder')  # SKF, Dollar, SFM
    is_module_monitor = fields.Boolean(related="project_id.is_module_monitor")
    module_branches = fields.Char(string='Branches', )
    module_version_ids = fields.Many2many(comodel_name='project.task.type', string='Odoo versions', help="")
