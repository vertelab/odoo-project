import json
import logging
import re

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ProjectciReport(http.Controller):
    @http.route(['/project/ci/report'], type='json', auth="public", methods=["POST"], csrf=False)
    def create_report(self, **payload):
        raw_data = request.httprequest.data
        data = json.loads(raw_data.decode('utf-8'))

        if data.get("id"):
            ci_id = int(data.get("id"))
            ci_branch_id = request.env["project.ci.branch"].sudo().browse(ci_id)
            ci_branch_id.sudo().write({"name":data.get("name"), "status": self.get_ci_status(data)})

            line_types = ["warnings", "errors", "criticals", "tracebacks"]

            for line_type in line_types:
                for line in data.get(line_type):
                    request.env["project.ci.branch.line"].sudo().create({"text":line, "line_type":self.get_ci_line_type(line_type), "project_ci_branch_id": ci_branch_id.id})
            request.env["project.ci.branch.line"].sudo().create({"text":data.get("full_log"), "line_type":"full_log", "project_ci_branch_id": ci_branch_id.id})
        
    def get_ci_status(self,data):
        if data.get("is_success") == "true":
            return "successful"
        return "failed"

    def get_ci_line_type(self,line_type):
        if line_type == "warnings":
            return "warning"
        elif line_type == "errors":
            return "error"
        elif line_type == "criticals":
            return "critical"
        elif line_type == "tracebacks":
            return "traceback"
        return line_type

