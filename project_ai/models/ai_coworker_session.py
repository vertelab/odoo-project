# -*- coding: utf-8 -*-
"""Kostnadskontext på ai.coworker.session — domänfält för project.

session-cost-context: `project_id`/`task_id` läggs via arv i bryggan
(core förblir domän-rent). `partner_id`/`pi_session_id`/
`cost_context_confirmed` ligger i ai_agent_core (res.partner = basmodul).

Registrerar även resolver-strategin "project_partner" i core-registret så
coworkers med `cost_context_partner_strategy = "project_partner"` får
partner härledd via task → projekt → partner / projekt → partner.
"""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


def _project_partner_strategy(session):
    """Resolver: hitta res.partner via task → project → partner,
    annars project → partner."""
    if session.task_id and session.task_id.project_id \
            and session.task_id.project_id.partner_id:
        session.partner_id = session.task_id.project_id.partner_id.id
    elif session.project_id and session.project_id.partner_id:
        session.partner_id = session.project_id.partner_id.id


try:
    from odoo.addons.ai_agent_core.models.ai_session import (
        register_cost_context_strategy)
    register_cost_context_strategy('project_partner', _project_partner_strategy)
except Exception as e:  # pragma: no cover — modulordning
    _logger.warning('kunde inte registrera project_partner-strategi: %s', e)


class AICoworkerSessionProject(models.Model):
    _inherit = 'ai.coworker.session'

    project_id = fields.Many2one(
        'project.project', string='Projekt', index=True,
        ondelete='set null',
        help='Projekt som sessionens kostnad belastar. Sätts via '
             'task-verktyg, chat-kontext eller cost_context_set.')
    task_id = fields.Many2one(
        'project.task', string='Uppgift', index=True,
        ondelete='set null',
        help='Uppgift (project.task) som sessionen arbetar med. '
             'Projekt och kund härleds indirekt via uppgiften.')

    def _capture_context(self, task=None, project=None, partner=None):
        """En enda skrivpunkt för kostnadskontext (D2).

        Härledning: project_id ← task.project_id; partner_id ←
        project.partner_id. Befintliga värden behålls om inget nytt ges
        ("senast arbetad kontext vinner" — inga nollställningar).
        """
        self.ensure_one()
        vals = {}
        if task:
            t = task if isinstance(task, models.BaseModel) else \
                self.env['project.task'].browse(int(task))
            if t:
                vals['task_id'] = t.id
                if t.project_id:
                    vals['project_id'] = t.project_id.id
        if project:
            p = project if isinstance(project, models.BaseModel) else \
                self.env['project.project'].browse(int(project))
            if p:
                vals['project_id'] = p.id
                if p.partner_id:
                    vals['partner_id'] = p.partner_id.id
        if partner:
            par = partner if isinstance(partner, models.BaseModel) else \
                self.env['res.partner'].browse(int(partner))
            if par:
                vals['partner_id'] = par.id
        if vals:
            self.write(vals)
        return self

    def _session_capture_context(self):
        """Core-hook: härled partner via resolver-strategin (project_ai).

        Anropas av openai_api-vägen när sessionen skapats/återfunnits.
        Självständig (anropar strategin direkt) så den fungerar även om
        coworkerns `cost_context_partner_strategy` inte satts än.
        """
        self.ensure_one()
        try:
            _project_partner_strategy(self)
        except Exception as e:
            _logger.warning('session capture (project) failed: %s', e)
        return self
