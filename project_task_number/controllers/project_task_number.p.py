
from collections import defaultdict
from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
import hashlib
import hmac
import json
import logging
import re

_logger = logging.getLogger(__name__)


# Input string
message = 'Heksan T/0003'

# Regular expression to extract T-number
match = re.search(r'T/\d{4}', message)

if match:
    t_number = match.group()
    print(t_number)  # Output: T/0003
else:
    print("No match found")



class GitHubWebHooks(http.Controller):

    @http.route(['/task/push'], type='json', auth="public", methods=["POST"], csrf=False)
    def task_push(self, **payload):
        """
        Hanterar inkommande webhook från GitHub.
        """

        self.check_signature()
        
        git_dict = self.get_git_data()

        self.find_project(git_dict)

         # ~ "ref":"refs/heads/18.0",
         # ~ "repository":{"id":855802141,"node_id":"R_kgDOMwKBHQ","name":"odoo-management-system","full_name":"vertelab/odoo-management-system","private":false,"owner":{"name":"vertelab","email":"support@vertel.se","login":"vertelab","id":10434571,"node_id":"MDEyOk9yZ2FuaXphdGlvbjEwNDM0NTcx","avatar_url":"https://avatars.githubusercontent.com/u/10434571?v=4","gravatar_id":"","url":"https://api.github.com/users/vertelab","html_url":"https://github.com/vertelab","followers_url":"https://api.github.com/users/vertelab/followers","following_url":"https://api.github.com/users/vertelab/following{/other_user}","gists_url":"https://api.github.com/users/vertelab/gists{/gist_id}","starred_url":"https://api.github.com/users/vertelab/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/vertelab/subscriptions","organizations_url":"https://api.github.com/users/vertelab/orgs","repos_url":"https://api.github.com/users/vertelab/repos","events_url":"https://api.github.com/users/vertelab/events{/privacy}","received_events_url":"https://api.github.com/users/vertelab/received_events","type":"Organization","user_view_type":"public","site_admin":false},"html_url":"https://github.com/vertelab/odoo-management-system","description":null,"fork":false,"url":"https://github.com/vertelab/odoo-management-system","forks_url":"https://api.github.com/repos/vertelab/odoo-management-system/forks","keys_url":"https://api.github.com/repos/vertelab/odoo-management-system/keys{/key_id}","collaborators_url":"https://api.github.com/repos/vertelab/odoo-management-system/collaborators{/collaborator}","teams_url":"https://api.github.com/repos/vertelab/odoo-management-system/teams","hooks_url":"https://api.github.com/repos/vertelab/odoo-management-system/hooks","issue_events_url":"https://api.github.com/repos/vertelab/odoo-management-system/issues/events{/number}","events_url":"https://api.github.com/repos/vertelab/odoo-management-system/events","assignees_url":"https://api.github.com/repos/vertelab/odoo-management-system/assignees{/user}",

          # ~ "head_commit":{
        # ~ "id":"6a1577789f5bb6e31b671998c2b72110d2253e18","tree_id":"3e4dc250f2c1d12a8d989292b504cdba114e677f","distinct":true,"message":"sadgfh","timestamp":"2025-02-11T12:03:06Z","url":"https://github.com/vertelab/odoo-management-system/commit/6a1577789f5bb6e31b671998c2b72110d2253e18","author":{"name":"Anders Wallenquist","email":"anders.wallenquist@vertel.se","username":"anderswallenquist"},
        # ~ "committer":{"name":"Anders Wallenquist","email":"anders.wallenquist@vertel.se","username":"anderswallenquist"},
        # ~ "added":[],
        # ~ "removed":[],
        # ~ "modified":["mgmtsystem_add_law/__manifest__.py"]
  # ~ }
       
        return {"status": "success", "message": "Webhook processed successfully"}

        # ~ except Exception as e:
            # ~ _logger.error("Error processing webhook: %s", str(e))
            # ~ return {"status": "error", "message": str(e)}

    def check_signature(self):
        secret = b"123"
        signature = request.httprequest.headers.get('X-Hub-Signature-256')
        computed_signature = 'sha256=' + hmac.new(secret, request.httprequest.data, hashlib.sha256).hexdigest()
        _logger.warning(f"Signature {signature=} {computed_signature=}")
        _logger.warning(f"headers {request.httprequest.headers=}")

        # ~ if not hmac.compare_digest(signature, computed_signature):
            # ~ return {"status": "error", "message": "Invalid signature"}
    
    def get_git_data(self):
        raw_payload = request.httprequest.data
        payload_dict = json.loads(raw_payload.decode('utf-8'))

            # Logga rådata för felsökning
        # ~ _logger.warning(f"Raw payload: {raw_payload}")

        # ~ _logger.warning(f"head_commit: {payload_dict.get('head_commit')=} {payload_dict.get('head_commit',{}).get('message')=}")
            
        match = re.search(r'T/\d{4}', message)

        git_dict = {
            "match": re.search(r'T/\d{4}', payload_dict.get('head_commit',{}).get('message')),
            "task_number": match.group(),
            "branch": payload_dict.get('ref','x/x/x').split('/')[2],
            "message": payload_dict.get('head_commit',{}).get('message'),
            "repo": payload_dict.get('repository',{}).get('name'),
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
                    '|', '|', '|',
                    ('email', '=', git_dict.get("committer_email")),  # Exact match
                    ('email', 'ilike', git_dict.get("committer_email")),  # Case-insensitive match
                    ('email', 'ilike', git_dict.get("committer_email").strip()),  # Case-insensitive with stripped input
                    ('email_normalized', '=', git_dict.get("committer_email"))  # Match normalized email (if applicable)
                ], limit=1)
        task = request.env['project.task'].sudo().search([('number','=',git_dict["task_number"])],limit=1)
        if not task:
            project = request.env['project.project'].sudo().search([('name','=',git_dict["repo"])],limit=1)
            if not project:
                project = request.env['project.project'].sudo().create({'name': git_dict["repo"]})
            # #if VERSION >= "15.0"
            user_ids = [(6,0,[user.id])] if user else None
            task = request.env['project.task'].sudo().create({'project_id': project.id, 'name': git_dict.get("message"),'number': git_dict["task_number"],'user_ids': user_ids })
            # #elif VERSION <= "14.0"
            user_id = user.id if user else None
            task = request.env['project.task'].sudo().create({'project_id': project.id, 'name': git_dict.get("message"),'number': git_dict["task_number"],'user_id': user_id })
            # #endif
        if not project:
            project = task.project_id
        author_id= user.id if user else request.env.user.id
        foo = task.sudo().message_post(
            body=f'Github post {git_dict.get("message")} [Branch={git_dict["branch"]}] Repo={git_dict["repo"]}<br/>{git_dict.get("committer_name")} {git_dict.get("committer_email")}<br/>Added={git_dict.get("added")}<br/>Removed={git_dict.get("removed")}<br/>Modified={git_dict.get("modified")}<br/>{git_dict.get("url")}',
            author_id=author_id,  
            # ~ message_type='comment',
            message_type='notification',
            subtype_xmlid='mail.mt_comment' 
        )
        _logger.warning(f'Success: {user=} {task=}  {project=} {git_dict.get("message")=} {git_dict["task_number"]=} {foo.body=} {foo.author_id.name=}')