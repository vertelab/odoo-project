import json
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    ai_plan = fields.Text(string='AI Plan')
    ai_usecase = fields.Html(string='AI Use Case', sanitize=False)
    ai_usecase_mermaid = fields.Text(string='AI Use Case Mermaid')

    def _get_project_planner_coworker(self):
        """Hitta Project Planner-coworkern (data-XML i project_ai_plan)."""
        return self.env['ai.coworker'].search(
            [('name', '=', 'Project Planner')], limit=1)

    def action_generate_ai_plan(self):
        """Generera ai_plan / ai_usecase / ai_usecase_mermaid via
        Project Planner-coworkern (brygg-standard: coworker.powerbox())."""
        self.ensure_one()
        coworker = self._get_project_planner_coworker()
        if not coworker:
            raise UserError(_(
                "Project Planner-coworkern saknas — installera "
                "project_ai_plan-data (ai_coworker_data.xml)."))

        prompt = (
            "Analysera projektuppgiften och generera implementationsplan, "
            "use case och Mermaid-diagram.\n\n"
            f"Uppgift: {self.name}\n"
            f"Beskrivning: {self.description or ''}\n"
            f"Projekt: {self.project_id.name or ''}\n\n"
            'Svara med JSON: {"ai_plan": "...", "ai_usecase": "...", "mermaid": "..."}'
        )
        try:
            result = coworker.powerbox(
                prompt=prompt, res_model=self._name, res_id=self.id)
        except Exception as e:
            _logger.error('Project Planner misslyckades: %s', e)
            raise UserError(_('Kunde inte generera: %s') % e)

        try:
            data = json.loads(str(result))
            self.write({
                'ai_plan': data.get('ai_plan', ''),
                'ai_usecase': data.get('ai_usecase', ''),
                'ai_usecase_mermaid': data.get('mermaid', ''),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('AI-plan genererad'),
                    'message': _('Plan, use case och Mermaid-diagram uppdaterade.'),
                    'type': 'success',
                },
            }
        except (json.JSONDecodeError, TypeError):
            # Fallback: spara hela svaret som plan (råtext)
            self.write({'ai_plan': str(result)[:4000]})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('AI-plan genererad (räformat)'),
                    'message': _('Svaret var inte JSON — sparades som plan.'),
                    'type': 'warning',
                },
            }
