# -*- coding: utf-8 -*-
"""Project Task Manager — ai.coworker-brygga för projektuppgifter.

Task 1.3: stage-slumpning per projekt (STAGE_PATTERNS från odoo_task.py).
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Mönster från /usr/share/pi/files/skills/odoo-vertel/odoo_task.py
STAGE_PATTERNS = {
    "analysis": ["analys", "analysis"],
    "design": ["design"],
    "ongoing": ["pågår", "pågående", "ongoing", "start"],
    "test": ["test"],
    "done": ["klar", "done", "ok"],
    "cancelled": ["avbruten", "cancelled"],
}


class ProjectTaskAICoworker(models.Model):
    _inherit = 'ai.coworker'

    @api.model
    def _project_task_find_stage(self, project_id, status_key):
        """Dynamiskt slå upp stage_id via namn-matchning mot projektets etapper."""
        patterns = STAGE_PATTERNS.get(status_key)
        if not patterns:
            return None

        stages = self.env['project.task.type'].search_read(
            [], fields=['id', 'name', 'project_ids'])
        project_stages = []
        global_stages = []
        for s in stages:
            proj_ids = s.get('project_ids') or []
            if not proj_ids:
                global_stages.append(s)
            elif project_id and project_id in proj_ids:
                project_stages.append(s)

        for pattern in patterns:
            for s in project_stages:
                if pattern.lower() in s['name'].lower():
                    return s['id']
        for pattern in patterns:
            for s in global_stages:
                if pattern.lower() in s['name'].lower():
                    return s['id']
        return None

    @api.model
    def _project_task_status_map(self):
        """Mappa en fritextstatus till STAGE_PATTERNS-nyckel."""
        return {
            'analysis': 'analysis',
            'design': 'design',
            'ongoing': 'ongoing',
            'in_progress': 'ongoing',
            'test': 'test',
            'testing': 'test',
            'done': 'done',
            'completed': 'done',
            'cancelled': 'cancelled',
            'canceled': 'cancelled',
            'closed': 'done',
        }

    @api.model
    def project_task_get(self, task_id):
        """Returnera task-info (JSON) för en projektuppgift."""
        task = self.env['project.task'].sudo().browse(task_id)
        if not task.exists():
            return {'error': 'Task %s not found' % task_id}
        return {
            'id': task.id,
            'name': task.name,
            'project_id': task.project_id.id if task.project_id else None,
            'project_name': task.project_id.name if task.project_id else '',
            'stage': task.stage_id.name if task.stage_id else '',
            'user_ids': [u.id for u in task.user_ids],
            'date_deadline': task.date_deadline.isoformat() if task.date_deadline else None,
            'priority': task.priority,
            'state': task.state,
            'description': (task.description or '')[:500],
        }

    @api.model
    def project_task_set_status(self, task_id, status):
        """Sätt task-status via stage-slumpning. Returnerar (ok, meddelande)."""
        task = self.env['project.task'].sudo().browse(task_id)
        if not task.exists():
            return False, 'Task %s not found' % task_id
        key = self._project_task_status_map().get(status.strip().lower())
        if not key:
            return False, 'Unknown status: %s' % status
        stage_id = self._project_task_find_stage(
            task.project_id.id, key)
        if not stage_id:
            return False, 'No stage found for status %r in project %s' % (
                status, task.project_id.name or task.project_id.id)
        task.write({'stage_id': stage_id})
        return True, 'Task %s moved to stage %s' % (task.name, status)
