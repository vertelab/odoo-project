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
    date = fields.Date('Date', required=True, default=fields.Date.today, tracking=True,
                       help="Start date of the contract.")
    
    def compute_status(self):
        for record in self:
            if record.project_ci_branch_ids:
                ci_branch_statuses = all([ci_branch_id.status == "successful" for ci_branch_id in record.project_ci_branch_ids])
                if ci_branch_statuses:
                    record.status = "successful"
                else:
                    record.status = "failed"
            else:
                record.status = "unknown"

                