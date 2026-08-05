
from odoo import conf, http, _, tools
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
import logging

from odoo.addons.project_github_webhook.controllers.github_webhooks import GitHubWebHooks

_logger = logging.getLogger(__name__)

p_file_sync = "Do not p-file sync"

class GitHubWebHooks(GitHubWebHooks):

    @http.route(['/task/push'], type='json', auth="public", methods=["POST"], csrf=False)
    def task_push(self, **payload):
        """
        Hanterar inkommande webhook från GitHub.
        """
        git_dict = self.get_git_data()
        user = request.env['res.users'].sudo().search([
                    '|',
                    ('email', '=', git_dict.get("committer_email")),  # Exact match
                    ('email_normalized', '=', git_dict.get("committer_email"))  # Match normalized email (if applicable)
                ], limit=1)
        if not user:
            user = request.env.ref("base.public_user")
        _logger.warning(f"{user=}")
        res_partner_id = request.env['res.partner'].sudo().search([("email", "=", git_dict.get("committer_email"))], limit=1)
        author_id=self.get_author_id(res_partner_id)
        _logger.warning(f"{author_id=}")
        task = self.find_task(git_dict)
        _logger.warning(f"{task=}")
        project = self.find_project(git_dict,task)
        _logger.warning(f"{project=}")
        if not task:
            if p_file_sync in git_dict["message"]:
                task = self.create_task(git_dict,user,project,"P-files Sync")
            else:
                task = self.create_task(git_dict,user,project)
        message_id = self.send_task_message(git_dict,task,author_id)
        _logger.warning(f'Success: {user=} {task=}  {project=} {git_dict.get("message")=} {git_dict["task_number"]=} {message_id.body=} {message_id.author_id.name=}')
            
        return {"status": "success", "message": "Webhook processed successfully"}

    def get_author_id(self, res_partner_id):
        _logger.warning(f"{res_partner_id.name=}")
        if res_partner_id and res_partner_id.name == "vertelbot":
            author_id = res_partner_id
        else:
            author_id = res_partner_id if res_partner_id else request.env.user.partner_id
        return author_id

    def create_task(self,git_dict,user,project,message=False):
        closing_stages = list(filter(lambda t: t.is_closed,project.type_ids))
        stage = list(filter(lambda t: t.name == "Klar!" or t.name == "Done",closing_stages))
        if not stage:
            if closing_stages:
                stage = closing_stages[0]
            else:
                stage = False
        else:
            stage = stage[0]

        user_ids = [(6,0,[user.id])]
        task_vals = {'project_id': project.id, 'name': git_dict.get("message"),'number': git_dict["task_number"] if git_dict["task_number"] else _("New"),'user_ids': user_ids, "stage_id": stage.id if stage else False}
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
            author_id=author_id.id,  
            message_type='comment',
            subtype_xmlid='mail.mt_note' 
        )
        return message_id