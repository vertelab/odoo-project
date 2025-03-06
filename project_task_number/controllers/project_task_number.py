
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

    def get_author_id(self, res_partner_id):
        if res_partner_id and res_partner_id.name == "vertelbot":
            author_id = res_partner_id
        else:
            author_id = user.partner_id.id if user else request.env.user.partner_id.id

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
        _logger.error(f"{user=}")
        res_partner_id = request.env['res.partner'].sudo().search([("email", "=", git_dict.get("committer_email"))], limit=1)
        author_id=get_author_id(res_partner_id)
        task = self.find_task(git_dict)
        _logger.error(f"{task=}")
        project = self.find_project(git_dict,task)
        _logger.error(f"{project=}")
        if not task:
            if p_file_sync in git_dict["message"]:
                task = self.create_task(git_dict,user,project,"P-files Sync")
            else:
                task = self.create_task(git_dict,user,project)
        message_id = self.send_task_message(git_dict,task,author_id)
        _logger.warning(f'Success: {user=} {task=}  {project=} {git_dict.get("message")=} {git_dict["task_number"]=} {message_id.body=} {message_id.author_id.name=}')
            
        return {"status": "success", "message": "Webhook processed successfully"}

    def create_task(self,git_dict,user,project,message=False):
        user_ids = [(6,0,[user.id])] if user else None
        task_vals = {'project_id': project.id, 'name': git_dict.get("message"),'number': git_dict["task_number"] if git_dict["task_number"] else _("New"),'user_ids': user_ids }
        if message:
            task_vals.update({"name": message})
        return  request.env['project.task'].sudo().create(task_vals)

    def find_task(self,git_dict):
        task = request.env['project.task'].sudo().search([('number','=',git_dict["task_number"])],limit=1)        
        if not task and p_file_sync in git_dict["message"]:
            task = request.env['project.task'].sudo().search([('name','=',"P-files Sync")],limit=1)            
        return task
    
    def find_project(self,git_dict,task):
        project = request.env['project.project'].sudo().search([('name','=',git_dict["repo"])],limit=1)        
        if task:
            project = task.project_id
        elif not project:
            project = request.env['project.project'].sudo().create({'name': git_dict["repo"]})
        return project

    def send_task_message(self,git_dict,task,author_id):
        message_id = task.sudo().message_post(
            body=f'Github post {git_dict.get("message")} [Branch={git_dict["branch"]}] Repo={git_dict["repo"]}<br/>{git_dict.get("committer_name")} {git_dict.get("committer_email")}<br/>Added={git_dict.get("added")}<br/>Removed={git_dict.get("removed")}<br/>Modified={git_dict.get("modified")}<br/>{git_dict.get("url")}',
            author_id=author_id,  
            message_type='notification',
            subtype_xmlid='mail.mt_comment' 
        )
        return message_id

    @http.route(['/sync/pfiles'], type='json', auth="public", methods=["POST"], csrf=False)
    def sync_pfiles(self, **payload):       
        check = self.check_signature()
        if check:
            return check
        git_dict = self.get_git_data()
        source_branch = git_dict.get("branch")
        pattern = "^[0-9]+.0$"
        match = re.search(pattern, source_branch)
        if (not match or not match.group()) or p_file_sync in git_dict.get("message"):
            return {"status": "success", "message": "Webhook Ignored"}
        project_sync_id = request.env["mail.channel"].sudo().create({"name": f"{uuid.uuid4()}","committer_email": git_dict.get("committer_email", "vertelbot@vertel.se")})
        project_sync_id.with_delay().sync(git_dict)
        return {"status": "success", "message": "Webhook P-file sync processed successfully."}

    # @http.route(['/sync/pfiles'], type='json', auth="public", methods=["POST"], csrf=False)
    # def sync_pfiles(self, **payload):       
    #     self.check_signature()
    #     git_dict = self.get_git_data()
    #     delete_when_done = True
    #     source_branch = git_dict.get("branch")
    #     pattern = "^[0-9]+.0$"
    #     match = re.search(pattern, source_branch)
    #     if (not match or not match.group()) or p_file_sync in git_dict.get("message"):
    #         return {"status": "success", "message": "Webhook Ignored"}
    #     files = self._get_files(git_dict)
    #     new_dir = str(uuid.uuid4())
    #     new_path = f"/var/lib/odoo/{new_dir}"
    #     new_repo_path = f"{new_path}/{git_dict.get('repo')}"
    #     self.run(["mkdir", f"{new_path}"], capture_output=True, text=True)
    #     self.run(["git", "clone", "-b", f"{source_branch}", f"git@github.com:vertelab/{git_dict.get('repo')}.git", f"{new_repo_path}"], capture_output=True, text=True)
    #     self.addpreprocess(new_repo_path)
    #     branch_list = self.run(["git", "-C", f"{new_repo_path}", "branch", "-r"], capture_output=True, text=True)
    #     pattern="(?:origin\/)([0-9]+.0)"
    #     branch_list = list(set(re.findall(pattern, branch_list.stdout)))
    #     _logger.error(f"{branch_list=}")
    #     for branch in branch_list:
    #         checkout_branch = self.run(["git", "-C", f"{new_repo_path}", "checkout", f"{branch}"], capture_output=True, text=True)
    #         _logger.info(f"{checkout_branch.stdout=}")
    #         for file in files:
    #             self.run(["git", "-C", f"{new_repo_path}", "checkout", f"{source_branch}", f"{file}"], capture_output=True, text=True)
    #         self.run(["git", "-C", f"{new_repo_path}", "add", "."], capture_output=True, text=True)
    #         self.run(["git", "-C", f"{new_repo_path}", "commit", "-m", f"odoobranchpfile {git_dict.get('repo')} from {source_branch}. {p_file_sync} {git_dict.get('task_number', '')}"], capture_output=True, text=True)
    #         self.run(["git", "-C", f"{new_repo_path}", "push"], capture_output=True, text=True)

    #     if delete_when_done:
    #         self.run(["rm", "-r", f"{new_path}"], capture_output=True, text=True)

    #     return {"status": "success", "message": "Webhook P-file sync processed successfully."}

    def run(self, *popenargs, **kwargs):
        ignore_errors=["nothing to commit, working tree clean"]
        errors=["error: pathspec", "Your local changes to the following files would be overwritten by checkout", "Host key verification failed."]
        result = subprocess.run(*popenargs, **kwargs)
        if result.returncode != 0 and not any([ignore_error in self.stderr_or_stdout(result) for ignore_error in ignore_errors]):
            for error in errors:
                if error in self.stderr_or_stdout(result):
                    self.subprocess_error(result)
            _logger.warning(f"The command '{' '.join(result.args)}' got this following error '{self.stderr_or_stdout(result)}'")
        return result

    def stderr_or_stdout(self,result):
        return result.stderr if result.stderr else result.stdout

    def addpreprocess(self, new_repo_path):
        if not os.path.exists("/usr/local/bin/preprocess"):
            raise Exception("Preprocess is not installed globally. Please install it with 'sudo pip install preprocess'.")
        if not os.path.exists(f"{new_repo_path}/.git/hooks/post-checkout"):
            self.run(["curl", "https://raw.githubusercontent.com/vertelab/odootools/common/post-checkout", "-o", f"{new_repo_path}/.git/hooks/post-checkout", "-s"], capture_output=True, text=True)
            self.run(["chmod", "a+x", f"{new_repo_path}/.git/hooks/post-checkout"], capture_output=True, text=True)

    def subprocess_error(self, result):
        _logger.error(f"{self.stderr_or_stdoutresult=}")
        self.send_email(result)
        delete_when_done = False

    def check_git_login(self):
        if self.run(["git", "config", "--global", "user.email"]).stdout != "vertelbot@vertel.se":
            self.run(["git", "config", "--global", "user.email", "vertelbot@vertel.se"], capture_output=True, text=True)
        if self.run(["git", "config", "--global", "user.email"]).stdout != "vertelbot":
            self.run(["git", "config", "--global", "user.name", "vertelbot"], capture_output=True, text=True)    
        
    # def send_email(self, result):
    #     git_dict = self.get_git_data()
    #     res_partner_id = request.env['res.partner'].sudo().search([("email", "=", git_dict.get("committer_email"))], limit=1)
    #     author_id = self.get_author_id(res_partner_id)
    #     message_id = task.sudo().message_post(
    #         body=f'{self.stderr_or_stdout(result)=}',
    #         subject='An error occurred when trying to sync P-files.',
    #         author_id=author_id,  
    #         message_type='email',
    #         subtype_xmlid='mail.mt_comment',
    #         email_from='vertelbot@vertel.se',
    #         email_to=f"{git_dict.get('committer_email', 'vertelbot@vertel.se')}",
    #     )
    #     return message_id

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

    def sync(self,git_dict):
        delete_when_done = True
        source_branch = git_dict.get("branch")
        pattern = "^[0-9]+.0$"
        match = re.search(pattern, source_branch)
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
            self.run(["git", "-C", f"{new_repo_path}", "commit", "-m", f"odoobranchpfile {git_dict.get('repo')} from {source_branch}. {p_file_sync} {git_dict.get('task_number', '')}"], capture_output=True, text=True)
            self.run(["git", "-C", f"{new_repo_path}", "push"], capture_output=True, text=True)

        if delete_when_done:
            self.run(["rm", "-r", f"{new_path}"], capture_output=True, text=True)
        
