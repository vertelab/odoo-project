from odoo import models, fields, api


class CalendarEvent(models.Model):
    _inherit = "mail.channel"

    calendar_event_id = fields.Many2one("calendar.event", string="Calendar Event")
    project_id = fields.Many2one("project.project", string="Project", related="calendar_event_id.project_id")

    def action_view_chat(self):
        self.ensure_one()
        menu_id = self.env.ref("mail.menu_root_discuss")
        action_id = self.env.ref("mail.action_discuss")
        link = "/web#action=%s&active_id=mail.channel_%s&menu_id=%s" % (action_id.id, self.id, menu_id.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': link,
        }

    def action_download_chat(self):
        return self.env.ref("mail_message_retrieve.chat_action_report").report_action(self)
