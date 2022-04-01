# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    calendar_event_id = fields.Many2one('calendar.event', readonly=True)

    # Writes a new post in the calendar that corresponds with the project task
    def create_event(self):
        for rec in self:
            _logger.warning("create_event")
            _logger.warning("create_event")
            _logger.warning("create_event")
            _logger.warning("create_event")
            _logger.warning("create_event")
            _logger.warning(f"rec.user_id:{rec.user_id}")
            arranger_id = rec.user_id.partner_id.id
            vals = {
                'name': rec.name,
                'description': _('Planned task'),
                'start': rec.date_deadline,
                'stop': rec.date_deadline,
                'allday': True,
                'privacy': 'confidential',
                'user_id': rec.user_id.id,
                'partner_ids': [(6, 0, [arranger_id])]
            }
            if rec.calendar_event_id and rec.user_id:
                rec.calendar_event_id.with_context(no_mail_to_attendees=True).write(vals)
            elif rec.calendar_event_id and not rec.user_id:
                # ~ rec.calendar_event_id.unlink()
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                _logger.warning("create_event IF ELSE")
                rec.calendar_event_id.write({
                    'user_id': False,
                    'partner_ids': [(5, 0, 0)],
                })
            else:
                rec.calendar_event_id = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(vals)

    # Calls create_event when the deadline or the assigned user on the project task is changed
    def write(self, values):
        res = super(ProjectTask, self).write(values)
        _logger.warning(f"write values{values}")
        # ~ if values.get('date_deadline') or values.get('user_id'):
        if 'date_deadline' in values or 'user_id' in values:
            self.create_event()
        return res
    
    # Unlinks the calendar post if the project task is removed
    def unlink(self):
        if self.calendar_event_id:
            self.calendar_event_id.unlink()
        res = super(ProjectTask, self).unlink()


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    partner_id = fields.Many2one('res.partner', string='Responsible Contact')
