from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectCIBranchLine(models.Model):
    _name = "project.ci.branch.line"
    _description = ""

    project_ci_branch_id = fields.Many2one(comodel_name="project.ci.branch")
    line_type = fields.Selection(
        selection=[("unknown", "Unknown"), ("warning", "Warning"), ("error", "Error"), ("critical","critical"), ("traceback", "Traceback"), ("full_log", "Full Log")],
        default="unknown", string="Line Type")
    text = fields.Text()
