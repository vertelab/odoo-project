from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging
from github import Github, Auth
import re
import base64

GITHUB_BASE_URL = 'https://api.github.com'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com'


_logger = logging.getLogger(__name__)

class projectProject(models.Model):
    _inherit = 'project.project'
    
    is_github_repo = fields.Boolean(string="Is Github Repo")

    git_owner = fields.Char(string="Git Owner") # example vertel,oca
    git_repo = fields.Char(string="Git Repo", help="For example odoo-l10n_se") # example l10n_se

    def _get_odoo_branches(self):
        if not (self.project_id.git_owner and task.project_id.git_repo):
            raise UserError(_("Owner and/or Repo is missing on project"))
        g = Github(auth=self.project_id.get_auth_token())
        try:
            repo = g.get_repo(f"{self.git_owner}/{self.git_repo}")
        except Exception as e:
            logger.warning(f"Could not read {self.git_owner}/{self.git_repo} {e}")
            return []
        return sorted([b.name for b in repo.get_branches() if re.match("^\d*[.]0$", b.name)])

    def _get_latest_branch(self,git_module):
        for branch in sorted(self._get_odoo_branches(), reverse = True):
            branch_url = f"{GITHUB_RAW_URL}/{self.git_owner}/{self.git_repo}/{branch}/"
            response = requests.get(f"{branch_url}/{git_module}/__manifest__.py")
            if response.status_code == 200:
                return branch
        return None
        
        
#TODO Issues
#TODO Pull Requests
        

    def get_auth_token(self):
        authToken = self.env["ir.config_parameter"].sudo().get_param('github_token')
        if not authToken:
            raise UserError("Github token missing, please create a parameter called github_token and paste an token.")
        return authToken

class projectTask(models.Model):
    _inherit = 'project.task'

    git_module = fields.Char(string="Git Module", help="For example, l10n_se_extended") # l10n_se_extended
    odoo_version = fields.Char(string='Odoo Version')
    is_github_repo = fields.Boolean(related="project_id.is_github_repo")

    is_module_odoo = fields.Boolean(string="Is Odoo module")
    module_author = fields.Char(string="Author") # example vertel,oca
    module_summary = fields.Char(string='Summary')
    module_category = fields.Char(string='Category') # Selection?
    module_website = fields.Char(string='Website')
    module_images  = fields.Char(string='Images', )
    module_license = fields.Char(string='Licence') # Selection
    module_maintainer = fields.Char(string='Maintainer',)
    module_depends = fields.Char(string='Depends')
    module_installable = fields.Boolean(string='Installable')
    module_application = fields.Boolean(string='Application')
    module_auto_install = fields.Boolean(string="Auto install")
    module_branches = fields.Char(string='Branches',)
    module_website_desc = fields.Html(string='Website Description',)
    
    def _get_github_response(self,filename):
        if not (self.git_module):
            raise UserError(_("Git Module is missing"))
        if not (self.project_id.git_owner and self.project_id.git_repo):
            raise UserError(_("Owner and/or Repo is missing on project"))
                
        g = Github(auth=Auth.Token(self.project_id.get_auth_token().strip()))
        try:
            repo = g.get_repo(f"{self.project_id.git_owner}/{self.project_id.git_repo}")
        except Exception as e:
            logger.warning(f"Could not read {self.project_id.git_owner}/{self.project_id.git_repo} {e}")
            return None

        # ~ raise UserError(sorted([b.name for b in repo.get_branches() if re.match("^\d*[.]0$", b.name)],key=float, reverse = True))
        for branch in sorted([b.name for b in repo.get_branches() if re.match("^\d*[.]0$", b.name)],key=float, reverse = True):
            branch_url = f"{GITHUB_RAW_URL}/{self.project_id.git_owner}/{self.project_id.git_repo}/{branch}"
            _logger.warning(f"get file---->   {branch_url}/{self.git_module}/{filename}")
            response = requests.get(f"{branch_url}/{self.git_module}/{filename}")
            if response.status_code == 200:
                self.write({'odoo_version': branch,})
                return response
        return None

    def _get_github_file(self,filename):
        response = self._get_github_response(filename)
        if response:
            return response.text

    def _get_github_content(self,filename):
        response = self._get_github_response(filename)
        if response:
            return response.content


    def get_module_info(self):
        for task in self:
            task.load_manifest()
            task.load_banner()
            task.load_index()

    def load_manifest(self,):
        # ~ https://pygithub.readthedocs.io/en/latest/examples/Repository.html
        # ~ https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
        for task in self:
            manifest = task._get_github_file('__manifest__.py')
            if manifest:
                manifest = eval(manifest)
            if manifest:
                task.write({
                    'name': manifest.get('name'),
                    'description': manifest.get('description',''),
                    'module_author': manifest.get('author',''),
                    'module_summary': manifest.get('summary',''),
                    'module_category': manifest.get('category',''),
                    'module_website': manifest.get('website',''),
                    'module_images': ','.join(manifest.get('images',[])),
                    'module_license': manifest.get('license',''),
                    'module_maintainer': manifest.get('maintainer',''),
                    'module_depends': ','.join(manifest.get('depends',[])),
                    'module_installable': manifest.get('installable',False),
                    'module_application': manifest.get('application',False),
                    'module_auto_install': manifest.get('auto_install',False),
                    # ~ 'module_branches': ','.join(branches),
                })
                task.message_post(body=f"""
                        Information updated for {task.odoo_version=}
                        """)

    def load_banner(self,):
        for task in self:
            banner = task.attachment_ids.filtered(lambda a: a.name == 'banner.png')
            if not banner:
                content = task._get_github_content('static/description/banner.png')
                if not content:
                    content = task._get_github_content('static/description/icon.png')
                if content:
                    banner = self.env["ir.attachment"].create(
                                {
                                    "name": 'banner.png',
                                    "res_id": task.id,
                                    "res_model": str(task._name),
                                    "datas": base64.encodebytes(content),
                                }
                            )
                    task.displayed_image_id = banner.id

    def load_index(self,):
        for task in self:
            index = task._get_github_file('static/description/index.html') 
            if index:
                task.module_website_desc = index
