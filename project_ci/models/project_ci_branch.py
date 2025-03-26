from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectCIBranch(models.Model):
    _name = "project.ci.branch"
    _description = ""

    name = fields.Char()
    project_ci_id = fields.Many2one(comodel_name="project.ci")
    project_id = fields.Many2one(comodel_name="project.project", related="project_ci_id.project_id")
    project_ci_branch_line_ids = fields.One2many(comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id")
    project_ci_branch_name_id = fields.Many2one(comodel_name="project.ci.branch.name")
    status = fields.Selection(
        selection=[("unknown", "Unknown"), ("successful", "Successful"), ("failed", "Failed")],
        default="unknown", string="Test Result")