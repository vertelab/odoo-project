
import json

from collections import defaultdict
from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class GitHubWebHooks(http.Controller):

    @http.route(['/task/push'], type='json', auth="public", website=True)
    def task_push(self, id=0, object=None, **post):
        _logger.warning(f"{id=}{object=}{post=}")
        return True
