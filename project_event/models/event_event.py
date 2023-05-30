from odoo import models, fields, api


class EventEvent(models.Model):
    _inherit = "event.event"

    project_id = fields.Many2one("project.project", string="Project")
    channel_id = fields.Many2one("mail.channel")