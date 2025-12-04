import subprocess
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    def create_project_ci(self):
        if self.project_ci_branch_name_ids:
            report_return_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', False)
            project_ci_id = self.env["project.ci"].create({"project_id":self.id})
            for branch in self.project_ci_branch_name_ids:
                project_ci_branch_id = self.env["project.ci.branch"].create({"project_ci_id": project_ci_id.id, "project_ci_branch_name_id": branch.id})
                command = ["ssh", "strand", "-t", "setup_odoo_test_machine", "-b", f"{branch.name}", "-p", f"{self.ci_project_name if self.ci_project_name else self.name}", "-i", f"{project_ci_branch_id.id}"]
                if self.ci_module_list:
                    command.append("-m")
                    command.append(f"{self.ci_module_list}")
                if self.ci_git_url:
                    command.append("-g")
                    command.append(f"{self.ci_git_url}")
                if self.ci_req_folder_path:
                    command.append("-r")
                    command.append(f"{self.ci_req_folder_path}")
                if report_return_url:
                    command.append("-u")
                    command.append(f"{report_return_url}")
                subprocess.Popen(command)
        else:
            raise UserError(f"No branches selected for {self.name}")
