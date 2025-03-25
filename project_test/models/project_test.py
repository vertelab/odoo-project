from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectTest(models.Model):
    _name = "project.test"
    _description = ""

    name = fields.Char()
    report = fields.Text()