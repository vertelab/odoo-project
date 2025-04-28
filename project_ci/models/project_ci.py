from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectCI(models.Model):
    _name = "project.ci"
    _description = "Project CI"
    _rec_name = 'create_date'

    project_id = fields.Many2one(comodel_name="project.project")
    project_ci_branch_ids = fields.One2many(comodel_name="project.ci.branch", inverse_name="project_ci_id")
    status = fields.Selection(
        selection=[("unknown", "Unknown"), ("successful", "Successful"), ("failed", "Failed")],
        default="unknown", string="Test Results", compute="compute_status")
    
    def compute_status(self):
        for record in self:
            if record.project_ci_branch_ids:
                ci_branch_statuses = [ci_branch_id.status for ci_branch_id in record.project_ci_branch_ids]
                if any([status == "failed" for status in ci_branch_statuses]):
                    record.status = "failed"
                elif any([status == "unknown" for status in ci_branch_statuses]):
                    record.status = "unknown"
                else:
                    record.status = "successful"
            else:
                record.status = "unknown"

                