# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'
    calendar_event_id = fields.Many2one('calendar.event',readonly=True)

    # Writes a new post in the calendar that corresponds with the project task
    def create_event(self):
        for rec in self:
            arranger_id = rec.user_id.partner_id.id
            vals = {
                        'name': rec.name,
                        'description': 'Planned event',
                        'start': rec.date_deadline,
                        'stop': rec.date_deadline,
                        'allday': True,
                        'privacy': 'confidential',
                        'user_id': rec.user_id.id,
                        'partner_ids':[(6, 0, [arranger_id] )]
                        }
            if rec.calendar_event_id:
                rec.calendar_event_id.with_context(no_mail_to_attendees=True).write(vals)
            else:
                rec.calendar_event_id = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(vals)

    # Calls create_event when the deadline or the assigned user on the project task is changed
    def write(self,values):
        res = super(ProjectTask,self).write(values)
        if values.get('date_deadline') or values.get('user_id'):
            self.create_event()
        return res
    
    # Unlinks the calendar post if the project task is removed
    def unlink(self):
        if self.calendar_event_id:
            self.calendar_event_id.unlink()
        res = super(ProjectTask,self).unlink()
