from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = "project.project"

    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count', compute_sudo=True)

    @api.depends('name')
    def _compute_meeting_count(self):
        for rec in self:
            rec.meeting_count = self.env["calendar.event"].search_count([
                ("project_id", "=", rec.id)
            ])

    def set_invitees(self):
        invitees = self.collaborator_ids.mapped("partner_id") + self.message_partner_ids
        return invitees

    def action_view_meeting(self):
        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        return {
            'name': _('Meetings'),
            'domain': [("project_id", "=", self.id)],
            'res_model': 'calendar.event',
            'type': 'ir.actions.act_window',
            'view_id': calendar_view.id,
            'views': [(calendar_view.id, 'calendar'), (False, 'tree'), (False, 'form')],
            'view_mode': 'calendar,tree,form',
            'context': {
                'default_project_id': self.id,
                'default_partner_ids': self.set_invitees().ids,
            }
        }

    def action_view_channel(self):
        channel_view = self.env.ref('project_event.project_mail_channel_view_kanban')
        return {
            'name': _('Discussion Channels'),
            'domain': [("project_id", "=", self.id)],
            'res_model': 'mail.channel',
            'type': 'ir.actions.act_window',
            'view_id': channel_view.id,
            'views': [(channel_view.id, 'kanban'), (False, 'tree'), (False, 'form')],
            'view_mode': 'kanban,tree,form',
        }

