import logging

from odoo import models, fields, api, _  # noqa:F401

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_start = fields.Date(string="Start Date")
    date_end2 = fields.Date(string="End Date")
