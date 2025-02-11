from odoo import models, api, fields
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class PrivacyLookupWizardLine(models.TransientModel):
    
    _inherit = 'privacy.lookup.wizard.line'

    project_lookup_type = fields.Selection([('customer','Customer'),('counterpart','Counterpart'),('stakeholders','Stakeholders')])
    project_id = fields.Many2one(comodel_name="project.project", string="Project")

    
    def action_confirm_manual_review(self):

        project_id = self.env.context.get("default_project_id")
        project_lookup_type = self.env.context.get("default_project_lookup_type")

        wizard_id = self.env.context.get("default_wizard_id")

        wizard_ids = self.env.context.get("default_wizard_ids")

        if wizard_ids: 

            wizard_ids = self.env["privacy.lookup.wizard"].browse(wizard_ids)

        return_to_project = {
                'name': 'return_to_project',
                'res_model': 'project.project',
                'res_id': project_id,
                'view_mode': 'form',
                'view_id': self.env.ref('project.edit_project').id,
                'target': 'current',
                'type': 'ir.actions.act_window',
            }

        if project_id:

            project_id = self.env["project.project"].browse(project_id)

            if project_lookup_type == "stakeholders" and wizard_ids:

                for wiz_id in wizard_ids:

                    if wizard_id == wiz_id.id:

                        wiz_id.is_reviewed = True


                if all([ wiz_id.is_reviewed for wiz_id in wizard_ids]) == False:

                    return project_id.action_privacy_lookup_stakeholders()  

            
            self._disable_project_button(project_id,project_lookup_type)

            return return_to_project            

        raise UserError("Context Empty")

    def _disable_project_button(self, project_id, project_lookup_type):

        match project_lookup_type:

            case "customer":
                project_id.message_post(body="Customers conflict of interest has been reviewed")
                project_id.is_reviewed_customer_COI = True

            case "counterpart":
                project_id.message_post(body="Counterparts conflict of interest has been reviewed")
                project_id.is_reviewed_counterpart_COI = True

            case "stakeholders":
                project_id.message_post(body="Stakeholders conflict of interests has been reviewed")
                project_id.is_reviewed_stakeholders_COI = True