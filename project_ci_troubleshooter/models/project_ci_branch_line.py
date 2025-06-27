from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectCIBranchLine(models.Model):
    _inherit = "project.ci.branch.line"
    
    def create_task(self):
        action = super(ProjectCIBranchLine, self).create_task()
        quest_id = self.env["ai.quest"].search([("ai_type", "=", "ci_troubleshooter")], limit=1)
        task_id = self.env["project.task"].browse(action["res_id"])
        quest_id.run(records=task_id, prompt=self.text)
        return action
        
