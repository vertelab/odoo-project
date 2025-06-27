from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class AIQuest(models.Model):
    _inherit = "ai.quest"
    
    ai_type = fields.Selection(
        selection_add=[('ci_troubleshooter', 'CI Troubleshooter')],
        ondelete={'ci_troubleshooter': 'cascade'}
    )
