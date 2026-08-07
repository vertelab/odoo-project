# -*- coding: utf-8 -*-
"""Smartknappar för AI-sessioner (tokens) på project.project.

session-cost-context 7.4: visar antal AI-sessioner + totala tokens för
projektet och leder till sessionslistan filtrerad på projektet.
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectProjectAI(models.Model):
    _inherit = 'project.project'

    ai_session_count = fields.Integer(
        'AI-sessioner', compute='_compute_ai_cost_stats',
        help='Antal AI-sessioner som belastar detta projekt.')
    ai_token_total = fields.Integer(
        'AI-tokens', compute='_compute_ai_cost_stats',
        help='Totala tokens (input+output) för AI-sessionerna på projektet.')

    @api.depends()
    def _compute_ai_cost_stats(self):
        Session = self.env['ai.coworker.session']
        for r in self:
            sessions = Session.search([('project_id', '=', r.id)])
            r.ai_session_count = len(sessions)
            r.ai_token_total = sum(
                (s.token_input or 0) + (s.token_output or 0)
                for s in sessions)

    def action_open_ai_sessions(self):
        """Öppna AI-sessionerna för projektet."""
        self.ensure_one()
        return {
            'name': 'AI-sessioner',
            'type': 'ir.actions.act_window',
            'res_model': 'ai.coworker.session',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('project_id', '=', self.id)],
            'context': {'search_default_project_id': self.id},
        }
