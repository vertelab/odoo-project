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
    project_ci_branch_line_warnings = fields.One2many(comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','warning')])
    project_ci_branch_line_errors = fields.One2many(comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','error')])
    project_ci_branch_line_criticlas = fields.One2many(comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','critical')])
    project_ci_branch_line_tracebacks = fields.One2many(comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','traceback')])
    project_ci_branch_line_full_log = fields.One2many(comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','full_log')])
    project_ci_branch_name_id = fields.Many2one(comodel_name="project.ci.branch.name")
    status = fields.Selection(
        selection=[("unknown", "Unknown"), ("successful", "Successful"), ("failed", "Failed")],
        default="unknown", string="Test Result")
    status_color_ball = fields.Selection(
        selection=[("unknown", "Unknown"), ("successful", "Successful"), ("failed", "Failed")],
        default="unknown", string="Test Result", compute="compute_status_color_ball")
    
    @api.depends("status")
    def compute_status_color_ball(self):
        for record in self:
            record.status_color_ball = record.status


    