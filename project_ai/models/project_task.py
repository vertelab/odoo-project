import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    """Projektuppgift — AI-fält.

    Fälten fylls av coworkerns AI-plan-arbetsflöde (skill_ai_plan_workflow):
    planen skrivs i ai_plan, funktionsbeskrivning och manuella tester i
    ai_usecase, och ett flöde i ai_usecase_mermaid.

    Knappen "Generera AI-plan" togs bort 2026-10-09 (T/12020) — planen
    skapas i dialog med användaren enligt skillens flöde, inte av en
    automatisk generering.
    """

    _inherit = 'project.task'

    ai_plan = fields.Text(string='AI Plan')
    ai_usecase = fields.Html(string='Use Case', sanitize=False)
    ai_usecase_mermaid = fields.Text(string='Use Case Mermaid')
