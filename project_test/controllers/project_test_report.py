import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ProjectTestReport(http.Controller):
    @http.route(['/project/test/report'], type='json', auth="public", methods=["POST"], csrf=False)
    def create_report(self, **payload):
        raw_data = request.httprequest.data
        data = json.loads(raw_data.decode('utf-8'))
        request.env["project.test"].sudo().create({"report": data})