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
    
    def create_task(self):
        task_id = self.env["project.task"].create({'name': self.text[-100:], 'description': self.text, 'project_id': self.project_ci_branch_id.project_id.id})
        action = {
            'type': 'ir.actions.act_window',
            'name': 'CI Task Wizard',
            'res_model': 'project.task',
            'view_mode': 'form',
            "res_id": task_id.id,
            'view_id': self.env.ref('project.view_task_form2').id,
            'target': 'new',
        }
        return action
