from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectTestBranch(models.Model):
    _name = "project.test.branch"
    _description = ""

    name = fields.Char()