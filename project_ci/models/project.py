import subprocess
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    is_odoo_project = fields.Boolean(string="is odoo project")
    project_ci_branch_name_ids = fields.Many2many(comodel_name="project.ci.branch.name")
    count_project_ci = fields.Integer(compute="compute_count_project_ci")
    count_project_ci_branch = fields.Integer(compute="compute_count_project_ci_branch")

    def project_ci_action(self):
        tree_view = self.env.ref('project_ci.project_ci_list_view')
        action = {
            'name': 'CI',
            'type': 'ir.actions.act_window',
            'res_model': 'project.ci',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (False, 'form')],
            'target': 'current',
            'domain': [("project_id", '=', self.id)],
        }
        return action

    def project_ci_branch_action(self):
        kanban_view = self.env.ref('project_ci.ci_branch_kanban_view')
        tree_view = self.env.ref('project_ci.project_ci_branch_list_view')
        action = {
            'name': 'CI Branch',
            'type': 'ir.actions.act_window',
            'res_model': 'project.ci.branch',
            'view_mode': 'kanban,tree,form',
            'views': [(kanban_view.id, 'kanban'), (tree_view.id, 'tree'), (False, 'form')],
            'target': 'current',
            'domain': [("project_id", '=', self.id)],
        }
        return action

    def compute_count_project_ci(self):
        for record in self:
            record.count_project_ci = record.env["project.ci"].search_count([("project_id", "=", record.id)])

    def compute_count_project_ci_branch(self):
        for record in self:
            record.count_project_ci_branch = record.env["project.ci.branch"].search_count([("project_id", "=", record.id)])
            

    def create_project_ci(self):
        if self.project_ci_branch_name_ids:
            project_ci_id = self.env["project.ci"].create({"project_id":self.id})
            for branch in self.project_ci_branch_name_ids:
                project_ci_branch_id = self.env["project.ci.branch"].create({"project_ci_id": project_ci_id.id, "project_ci_branch_name_id": branch.id})
                subprocess.Popen(["ssh", "strand", "-t", "setup_odoo_test_machine", "-b", f"{branch.name}", "-p", f"{self.name}", "-i", f"{project_ci_branch_id.id}"])
        else:
            raise UserError(f"No branches selected for {self.name}")