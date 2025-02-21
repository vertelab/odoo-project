
from collections import defaultdict
from odoo import conf, http, _, tools
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
import hashlib
import hmac
import json
import logging
import re
import subprocess
import uuid
import os

_logger = logging.getLogger(__name__)

class GitHubWebHooks(http.Controller):

    @http.route(['/task/push'], type='json', auth="public", methods=["POST"], csrf=False)
    def task_push(self, **payload):
        """
        Hanterar inkommande webhook från GitHub.
        """
        self.check_signature()
        git_dict = self.get_git_data()
        self.find_project(git_dict)
        return {"status": "success", "message": "Webhook processed successfully"}

    @http.route(['/sync/pfiles'], type='json', auth="public", methods=["POST"], csrf=False)
    def sync_pfiles(self, **payload):       
        self.check_signature()
        git_dict = self.get_git_data()
        source_branch = git_dict.get("branch")
        pattern = "^[0-9]+.0$"
        match = re.search(pattern, source_branch)
        if (not match or not match.group()) or "Do not p-file sync" in git_dict.get("message"):
            return {"status": "success", "message": "Webhook Ignored"}
        files = self._get_files(git_dict)
        new_dir = str(uuid.uuid4())
        new_path = f"/var/lib/odoo/{new_dir}"
        new_repo_path = f"{new_path}/{git_dict.get('repo')}"
        self.run(["mkdir", f"{new_path}"], capture_output=True, text=True)
        self.run(["git", "clone", "-b", f"{source_branch}", f"git@github.com:vertelab/{git_dict.get('repo')}.git", f"{new_repo_path}"], capture_output=True, text=True)
        self.addpreprocess(new_repo_path)
        branch_list = self.run(["git", "-C", f"{new_repo_path}", "branch", "-r"], capture_output=True, text=True)
        pattern="(?:origin\/)([0-9]+.0)"
        branch_list = list(set(re.findall(pattern, branch_list.stdout)))
        _logger.error(f"{branch_list=}")
        for branch in branch_list:
            checkout_branch = self.run(["git", "-C", f"{new_repo_path}", "checkout", f"{branch}"], capture_output=True, text=True)
            _logger.info(f"{checkout_branch.stdout=}")
            for file in files:
                self.run(["git", "-C", f"{new_repo_path}", "checkout", f"{source_branch}", f"{file}"], capture_output=True, text=True)
            self.run(["git", "-C", f"{new_repo_path}", "add", "."], capture_output=True, text=True)
            self.run(["git", "-C", f"{new_repo_path}", "commit", "-m", f"odoobranchpfile {git_dict.get('repo')} from {source_branch}. Do not p-file sync {git_dict.get('task_number', '')}"], capture_output=True, text=True)
            self.run(["git", "-C", f"{new_repo_path}", "push"], capture_output=True, text=True)

        self.run(["rm", "-r", f"{new_path}"], capture_output=True, text=True)

        return {"status": "success", "message": "Webhook P-file sync processed successfully."}

    def run(self, *popenargs, **kwargs):
        ignore_errors=["nothing to commit, working tree clean"]
        result = subprocess.run(*popenargs, **kwargs)
        if result.returncode != 0 and not any([ignore_error in result.stdout for ignore_error in ignore_errors]):
            if "error: pathspec" in result.stderr:
                self.create_missing_dirs(result)
            _logger.warning(f"The command '{' '.join(result.args)}' got this following error '{result.stderr if result.stderr else result.stdout}'")
        return result

    def addpreprocess(self, new_repo_path):
        if not os.path.exists("/usr/local/bin/preprocess"):
            raise Exception("Preprocess is not installed globally. Please install it with 'sudo pip install preprocess'.")
        if not os.path.exists(f"{new_repo_path}/.git/hooks/post-checkout"):
            self.run(["curl", "https://raw.githubusercontent.com/vertelab/odootools/common/post-checkout", "-o", f"{new_repo_path}/.git/hooks/post-checkout", "-s"], capture_output=True, text=True)
            self.run(["chmod", "a+x", f"{new_repo_path}/.git/hooks/post-checkout"], capture_output=True, text=True)

    def create_missing_dirs(self, result):
        pass

    def check_git_login(self):
        if self.run(["git", "config", "--global", "user.email"]).stdout != "vertelbot@vertel.se":
            self.run(["git", "config", "--global", "user.email", "vertelbot@vertel.se"], capture_output=True, text=True)
        if self.run(["git", "config", "--global", "user.email"]).stdout != "vertelbot":
            self.run(["git", "config", "--global", "user.name", "vertelbot"], capture_output=True, text=True)

    def check_signature(self):
        secret = tools.config.get("githook_secret", "").encode("utf-8")
        if secret == b'':
            _logger.error(f"No secret in odoo.conf for githooks!!!!!!!")
        signature = request.httprequest.headers.get('X-Hub-Signature-256')
        computed_signature = 'sha256=' + hmac.new(secret, request.httprequest.data, hashlib.sha256).hexdigest()
        _logger.warning(f"Signature {signature=} {computed_signature=}")
        _logger.warning(f"headers {request.httprequest.headers=}")

        if not hmac.compare_digest(signature, computed_signature):
            return {"status": "error", "message": "Invalid signature"}

    def get_git_data(self):
        raw_payload = request.httprequest.data
        payload_dict = json.loads(raw_payload.decode('utf-8'))
            
        message = payload_dict.get('head_commit',{}).get('message')
        match = re.search(r'T/\d{4}', message)
        git_dict = {
            "match": re.search(r'T/\d{4}', payload_dict.get('head_commit',{}).get('message')),
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
    
    def find_project(self,git_dict):
        project = None
        user = request.env['res.users'].sudo().search([
                    '|',
                    ('email', '=', git_dict.get("committer_email")),  # Exact match
                    ('email_normalized', '=', git_dict.get("committer_email"))  # Match normalized email (if applicable)
                ], limit=1)
        _logger.error(f"{user=}")
        task = request.env['project.task'].sudo().search([('number','=',git_dict["task_number"])],limit=1)
        _logger.error(f"{task=} {git_dict['task_number']=}")
        if not task:
            project = request.env['project.project'].sudo().search([('name','=',git_dict["repo"])],limit=1)
            if not project:
                project = request.env['project.project'].sudo().create({'name': git_dict["repo"]})
            user_ids = [(6,0,[user.id])] if user else None
            task = request.env['project.task'].sudo().create({'project_id': project.id, 'name': git_dict.get("message"),'number': git_dict["task_number"] if git_dict["task_number"] else _("New"),'user_ids': user_ids })
        if not project:
            project = task.project_id
        author_id= user.partner_id.id if user else request.env.user.partner_id.id
        message_id = task.sudo().message_post(
            body=f'Github post {git_dict.get("message")} [Branch={git_dict["branch"]}] Repo={git_dict["repo"]}<br/>{git_dict.get("committer_name")} {git_dict.get("committer_email")}<br/>Added={git_dict.get("added")}<br/>Removed={git_dict.get("removed")}<br/>Modified={git_dict.get("modified")}<br/>{git_dict.get("url")}',
            author_id=author_id,  
            # ~ message_type='comment',
            message_type='notification',
            subtype_xmlid='mail.mt_comment' 
        )
        _logger.warning(f'Success: {user=} {task=}  {project=} {git_dict.get("message")=} {git_dict["task_number"]=} {message_id.body=} {message_id.author_id.name=}')


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
        
