import hashlib
import hmac
import json
import logging
import re
import subprocess
import uuid
import os

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

p_file_sync = "Do not p-file sync"
delete_when_done = True

class MailChannel(models.Model):
    # #if VERSION >= "18.0"
    _inherit = "discuss.channel"
    # #elif VERSION <= "17.0"
    _inherit = "mail.channel"
    # #endif
    _description = ""

    committer_email = fields.Char()

    def run(self, *popenargs, **kwargs):
        ignore_errors=["nothing to commit, working tree clean"]
        errors=["error: pathspec", "Your local changes to the following files would be overwritten by checkout", "Host key verification failed."]
        result = subprocess.run(*popenargs, **kwargs)
        _logger.error(f"{result=}")
        if result.returncode != 0 and not any([ignore_error in self.stderr_or_stdout(result) for ignore_error in ignore_errors]):
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
        _logger.error(f"{self.stderr_or_stdout(result)=}")
        self.send_email(result)
        delete_when_done = False

    def check_git_login(self):
        if "vertelbot@vertel.se" not in self.run(["git", "config", "--global", "user.email"], capture_output=True, text=True).stdout:
            self.run(["git", "config", "--global", "user.email", "vertelbot@vertel.se"], capture_output=True, text=True)
        if "vertelbot" not in self.run(["git", "config", "--global", "user.email"], capture_output=True, text=True).stdout:
            self.run(["git", "config", "--global", "user.name", "vertelbot"], capture_output=True, text=True)    
    
    def send_email(self, result):
        res_partner_id = self.env['res.partner'].sudo().search([("email", "=", self.committer_email)], limit=1)
        author_id = self.get_author_id(res_partner_id)
        message_id = self.sudo().message_post(
            body=f'{self.stderr_or_stdout(result)=}',
            subject='An error occurred when trying to sync P-files.',
            author_id=author_id,  
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            email_from='vertelbot@vertel.se',
            email_to=f"{self.committer_email if self.committer_email else 'vertelbot@vertel.se'}",
        )
        return message_id

    def get_author_id(self, res_partner_id):
        if res_partner_id and res_partner_id.name == "vertelbot":
            author_id = res_partner_id
        else:
            author_id = res_partner_id.id if res_partner_id else self.env.user.partner_id.id

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
        source_branch = git_dict.get("branch")
        files = self._get_files(git_dict)
        self.check_git_login()
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
