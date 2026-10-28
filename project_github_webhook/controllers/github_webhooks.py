
from odoo import conf, http, _, tools
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from werkzeug.exceptions import Forbidden
import hashlib
import hmac
import json
import logging
import re

_logger = logging.getLogger(__name__)

class GitHubWebHooks(http.Controller):

    def check_signature(self):
        """Verify the GitHub webhook HMAC signature.

        Raises Forbidden on any failure, so it cannot be bypassed by
        ignoring the return value. Callers that still write
        ``if self.check_signature(): return ...`` keep working: the
        method returns None on success and never returns on failure.
        """
        secret = tools.config.get("githook_secret", "").encode("utf-8")
        if secret == b'':
            _logger.error("No githook_secret in odoo.conf - rejecting webhook")
            raise Forbidden("Webhook secret not configured")

        signature = request.httprequest.headers.get('X-Hub-Signature-256')
        if not signature:
            _logger.error("Webhook missing X-Hub-Signature-256 header - rejecting")
            raise Forbidden("Missing signature header")

        computed_signature = 'sha256=' + hmac.new(secret, request.httprequest.data, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(signature, computed_signature):
            _logger.error("Webhook signature mismatch - rejecting")
            raise Forbidden("Invalid signature")

    def get_git_data(self):
        # Signature verification is baked in here so no subclass can reach
        # the payload without passing it. This is the only place the raw
        # body is read; do not add another entry point that skips it.
        self.check_signature()

        raw_payload = request.httprequest.data
        payload_dict = json.loads(raw_payload.decode('utf-8'))
            
        message = payload_dict.get('head_commit',{}).get('message')
        match = re.search(r'T/\d{4}', message)
        git_dict = {
            "task_number": match.group() if match else "",
            "branch": payload_dict.get('ref','x/x/x').split('/')[2],
            "message": payload_dict.get('head_commit',{}).get('message'),
            "repo": payload_dict.get('repository',{}).get('name'),
            "commits": payload_dict.get('commits', []),
            "committer_name": payload_dict.get('head_commit',{}).get('committer',{}).get('name'),
            "committer_email": payload_dict.get('head_commit',{}).get('committer',{}).get('email'),
            "added": payload_dict.get('head_commit',{}).get('added',[]),
            "removed": payload_dict.get('head_commit',{}).get('removed',[]),
            "modified": payload_dict.get('head_commit',{}).get('modified',[]),
            "url": payload_dict.get('head_commit',{}).get('url',""),
        }

        return git_dict