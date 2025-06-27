from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectCIBranch(models.Model):
    _name = "project.ci.branch"
    _description = "Project CI Branch"


    name = fields.Char()
    ip_address = fields.Char(string="IP Address")
    project_ci_id = fields.Many2one(comodel_name="project.ci")
    project_id = fields.Many2one(comodel_name="project.project", related="project_ci_id.project_id")
    project_ci_branch_line_ids = fields.One2many(
        comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id")

    @api.depends('project_ci_branch_line_ids')
    def _compute_project_ci_branch_line(self):
        for rec in self:
            rec.project_ci_branch_line_count = len(rec.project_ci_branch_line_ids)

    project_ci_branch_line_count = fields.Integer(compute=_compute_project_ci_branch_line)
    project_ci_branch_line_warnings = fields.One2many(
        comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','warning')])
    project_ci_branch_line_errors = fields.One2many(
        comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id", domain=[('line_type','=','error')])
    project_ci_branch_line_criticlas = fields.One2many(
        comodel_name="project.ci.branch.line",
        inverse_name="project_ci_branch_id", domain=[('line_type','=','critical')]
    )
    project_ci_branch_line_tracebacks = fields.One2many(
        comodel_name="project.ci.branch.line",
        inverse_name="project_ci_branch_id", domain=[('line_type','=','traceback')]
    )
    project_ci_branch_line_full_log = fields.One2many(
        comodel_name="project.ci.branch.line", inverse_name="project_ci_branch_id",
        domain=[('line_type','=','full_log')]
    )
    project_ci_branch_name_id = fields.Many2one(comodel_name="project.ci.branch.name")
    
    status = fields.Selection(
        selection=[("unknown", "Unknown"), ("successful", "Successful"), ("failed", "Failed")],
        default="unknown", string="Test Result")
    
    kanban_state = fields.Selection([('normal', 'In Progress'), ('done', 'Done'), ('blocked', 'Blocked')],
                                    default='normal', compute='_compute_kanban_state')

    @api.depends("status")
    def _compute_kanban_state(self):
        for record in self:
            kanban_state = 'normal'
            if record.status == 'successful':
                kanban_state = 'done'
            elif record.status == 'failed':
                kanban_state = 'blocked'
            record.kanban_state = kanban_state


    
