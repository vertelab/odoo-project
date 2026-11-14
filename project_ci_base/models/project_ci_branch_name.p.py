from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProjectCIBranchName(models.Model):
    _name = "project.ci.branch.name"
    _description = "Project CI Branch Name"

    name = fields.Char()
