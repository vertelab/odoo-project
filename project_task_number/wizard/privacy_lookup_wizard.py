from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class PrivacyLookupWizard(models.TransientModel):
    
    _inherit = 'privacy.lookup.wizard'

    project_lookup_type = fields.Selection([('customer','Customer'),('counterpart','Counterpart'),('stakeholders','Stakeholders')])
    project_id = fields.Many2one(comodel_name="project.project", string="Project")
    wizard_ids = fields.Char(default=False)
    is_reviewed = fields.Boolean(default=False)


    def action_open_lines(self):
        self.ensure_one()
        action = super().action_open_lines()

        self.wizard_ids = self.env.context.get("default_wizard_ids")

        action["context"] = {
            'default_project_lookup_type': str(self.project_lookup_type),
            'default_project_id': self.project_id.id,
            'default_wizard_id': self.id
        }

        if self.wizard_ids:

            action["context"].update({'default_wizard_ids': list(map(int,self.wizard_ids.split(",")))})

        return action