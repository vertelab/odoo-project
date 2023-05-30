from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    project_id = fields.Many2one("project.project", string="Project")

    def action_view_chat(self):
        self.ensure_one()
        menu_id = self.env.ref("mail.menu_root_discuss")
        action_id = self.env.ref("mail.action_discuss")
        if self.videocall_channel_id:
            link = "/web#action=%s&active_id=mail.channel_%s&menu_id=%s" % (
                action_id.id, self.videocall_channel_id.id, menu_id.id
            )
            return {
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': link,
            }

    def action_videocall_channel(self):
        if not self.videocall_location:
            raise ValidationError(_('You Should add a Meeting Link First.'))
        if not self.videocall_channel_id:
            self._create_videocall_channel()
        if self.videocall_channel_id:
            self.videocall_channel_id.write({"calendar_event_id": self.id})
