import subprocess
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    is_odoo_project = fields.Boolean(string="is odoo project")
    project_test_branch_ids = fields.Many2many(comodel_name="project.test.branch")

    def create_project_tests(self):
        for record in self:
            if record.project_test_branch_ids:
                for branch in record.project_test_branch_ids:
                    subprocess.run(["ssh", "strand", "-t", "setup_odoo_test_machine", "-b", f"{branch.name}", "-p", f"{record.name}", "&"], capture_output=True, text=True)
            else:
                raise UserError(f"No branches selected for {record.name}")