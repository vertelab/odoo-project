# -*- coding: utf-8 -*-
"""Smartknapp för AI-sessioner (tokens) på res.partner (kundkortet).

session-cost-context 7.5: visar antal AI-sessioner + totala tokens för
kunden och leder till sessionslistan filtrerad på partner_id.
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartnerAI(models.Model):
    _inherit = 'res.partner'

    ai_session_count = fields.Integer(
        'AI-sessioner', compute='_compute_ai_cost_stats',
        help='Antal AI-sessioner som belastar kunden.')
    ai_token_total = fields.Integer(
        'AI-tokens', compute='_compute_ai_cost_stats',
        help='Totala tokens (input+output) för AI-sessionerna på kunden.')

    @api.depends()
    def _compute_ai_cost_stats(self):
        Session = self.env['ai.coworker.session']
        for r in self:
            sessions = Session.search([('partner_id', '=', r.id)])
            r.ai_session_count = len(sessions)
            r.ai_token_total = sum(
                (s.token_input or 0) + (s.token_output or 0)
                for s in sessions)

    def action_open_ai_sessions(self):
        """Öppna AI-sessionerna för kunden."""
        self.ensure_one()
        return {
            'name': 'AI-sessioner',
            'type': 'ir.actions.act_window',
            'res_model': 'ai.coworker.session',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
            'context': {'search_default_partner_id': self.id},
        }
