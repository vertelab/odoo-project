
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

p_file_sync = "Do not p-file sync"
delete_when_done = True

class GitHubWebHooks(http.Controller):

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
        #"match": re.search(r'T/\d{4}', payload_dict.get('head_commit',{}).get('message')),
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

    def get_author_id(self, res_partner_id):
        if res_partner_id and res_partner_id.name == "vertelbot":
            author_id = res_partner_id
        else:
            author_id = res_partner_id if res_partner_id else request.env.user.partner_id
        return author_id

    @http.route(['/task/push'], type='json', auth="public", methods=["POST"], csrf=False)
    def task_push(self, **payload):
        """
        Hanterar inkommande webhook från GitHub.
        """
        self.check_signature()
        git_dict = self.get_git_data()
        user = request.env['res.users'].sudo().search([
                    '|',
                    ('email', '=', git_dict.get("committer_email")),  # Exact match
                    ('email_normalized', '=', git_dict.get("committer_email"))  # Match normalized email (if applicable)
                ], limit=1)
        if not user:
            user = request.env.ref("base.public_user")
        res_partner_id = request.env['res.partner'].sudo().search([("email", "=", git_dict.get("committer_email"))], limit=1)
        author_id=self.get_author_id(res_partner_id)
        task = project = False
        if git_dict.get("task_number"):
            task,project = self.has_task_number(git_dict)
        elif p_file_sync in git_dict["message"]:
            task,project = self.is_sync_message(git_dict,user)
        else:
            project = self.find_project(git_dict)
            task = self.create_task(git_dict,user,project)
        if not project or not task:
            _logger.error(f'Failure: {user=} {task=} {project=} {git_dict.get("message")=} {git_dict["task_number"]=} {message_id.body=} {message_id.author_id.name=}')
            return {"status": "failure", "message": f"Webhook processed successfully, but {project=} or {task=} not set."}
        message_id = self.send_task_message(git_dict,task,author_id)
        _logger.warning(f'Success: {user=} {task=}  {project=} {git_dict.get("message")=} {git_dict["task_number"]=} {message_id.body=} {message_id.author_id.name=}')    
        return {"status": "success", "message": "Webhook processed successfully"}

    def create_task(self,git_dict,user,project,message=False):
        task_vals = {'project_id': project.id, 'name': git_dict.get("message"),'number': git_dict["task_number"] if git_dict["task_number"] else _("New"),'user_id': user.id if user else None }
        if message:
            task_vals.update({"name": message})
        return  request.env['project.task'].sudo().create(task_vals)

    def is_sync_message(self,git_dict,user):
        project = self.find_project(git_dict)
        task = request.env['project.task'].sudo().search([('name','=',"P-files Sync"),('project_id',"=",project.id)],limit=1)
        if not task:
            task = self.create_task(git_dict,user,project,"P-files Sync")
        return task, project

    def has_task_number(self,git_dict):
        task = request.env['project.task'].sudo().search([('number','=',git_dict["task_number"])],limit=1)
        project = self.find_project(git_dict,task)
        return task, project

    def find_project(self,git_dict,task=False):
        project = request.env['project.project'].sudo().search([('name','=',git_dict["repo"])],limit=1)
        if task:
            project = task.project_id           
        
        if not project:
            project = request.env['project.project'].sudo().create({'name': git_dict["repo"]})

        return project

    def send_task_message(self,git_dict,task,author_id):
        message_id = task.sudo().message_post(
            body=f'Github post {git_dict.get("message")} [Branch={git_dict["branch"]}] Repo={git_dict["repo"]}<br/>{git_dict.get("committer_name")} {git_dict.get("committer_email")}<br/>Added={git_dict.get("added")}<br/>Removed={git_dict.get("removed")}<br/>Modified={git_dict.get("modified")}<br/>{git_dict.get("url")}',
            author_id=author_id.id,  
            message_type='notification',
            subtype_xmlid='mail.mt_comment' 
        )
        return message_id

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
        _logger.error(f"{request.httprequest.headers=}")
        _logger.error(f"{type(request.httprequest.headers)=}")
        _logger.error(f"{dict(request.httprequest.headers)=}")
        project_sync_id.with_delay(description=json.dumps(dict(request.httprequest.headers))).sync(git_dict,files)
        return {"status": "success", "message": "Webhook P-file sync processed successfully."}
