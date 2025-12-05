import logging
import re
import uuid

from odoo import conf, http, _, tools
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request

from odoo.addons.project_github_webhook.controllers.github_webhooks import GitHubWebHooks

_logger = logging.getLogger(__name__)

p_file_sync = "Do not p-file sync"

class GitHubWebHooks(GitHubWebHooks):

    def _get_files(self,git_dict):
        strings_of_interest = [".p.", "index.html", ".png", ".jpg"]
        files = []
        for commit in git_dict.get('commits'):
            for string in strings_of_interest:
                files.extend(filter(lambda added: string in added,commit.get("added", [])))
                files.extend(filter(lambda modified: string in modified,commit.get("modified", [])))
        files = list(set(files))
        _logger.error(f"{files=}") 
        return files

    @http.route(['/sync/pfiles'], type='json', auth="public", methods=["POST"], csrf=False)
    def sync_pfiles(self, **payload):       
        check = self.check_signature()
        if check:
            return check
        git_dict = self.get_git_data()
        files = self._get_files(git_dict)
        contains_p_files = any([".p." in file for file in files])
        source_branch = git_dict.get("branch")
        pattern = "^[0-9]+.0$"
        match = re.search(pattern, source_branch)
        if (not match or not match.group()) or p_file_sync in git_dict.get("message") or not contains_p_files:
            return {"status": "success", "message": "Webhook Ignored"}
        project_sync_id = request.env["mail.channel"].sudo().create({"name": f"{uuid.uuid4()}","committer_email": git_dict.get("committer_email", "vertelbot@vertel.se")})
        # project_sync_id.with_delay().sync(git_dict,files)
        project_sync_id.sync(git_dict,files)
        return {"status": "success", "message": "Webhook P-file sync processed successfully."}
