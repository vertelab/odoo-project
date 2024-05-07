from odoo import models, fields, api, _
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


    def get_auth_token(self):
        authToken = self.env["ir.config_parameter"].sudo().get_param('github_token')
        if not authToken:
            raise UserError("Github token missing, please create a parameter called github_token and paste an token.")
        return authToken

    def _get_odoo_branches(self,git_owner=None,git_repo=None):
        if not (git_owner and git_repo):
            git_owner = self.git_owner
            git_repo  = self.git_repo
        if not (git_owner and git_repo):
            raise UserError(_(f"Owner and/or Repo is missing on project {git_owner=} {git_repo=} [branches]"))
        g = Github(auth=Auth.Token(self.get_auth_token().strip()))
        try:
            repo = g.get_repo(f"{git_owner}/{git_repo}")
        except Exception as e:
            _logger.warning(f"Could not read {git_owner}/{git_repo} {e}")
            return []
        return sorted([b.name for b in repo.get_branches() if re.match("^\d*[.]0$", b.name)],key=float)

    def _get_latest_branch(self,git_module,git_owner=None,git_repo=None):
        if not (git_owner and git_repo):
            git_owner = self.git_owner
            git_repo  = self.git_repo
        for branch in sorted(self._get_odoo_branches(git_owner,git_repo), reverse = True):
            branch_url = f"{GITHUB_RAW_URL}/{git_owner}/{git_repo}/{branch}/"
            response = requests.get(f"{branch_url}/{git_module}/__manifest__.py")
            if response.status_code == 200:
                return branch
        return None
 
    def _get_git_contents(self,git_owner=None,git_repo=None):
        if not (git_owner and git_repo):
            git_owner = self.git_owner
            git_repo  = self.git_repo
        if not (git_owner and git_repo):
            raise UserError(_("Owner and/or Repo is missing on project [content]"))
        g = Github(auth=Auth.Token(self.get_auth_token().strip()))
        try:
            repo = g.get_repo(f"{git_owner}/{git_repo}")
        except Exception as e:
            logger.warning(f"Could not read {git_owner}/{git_repo} {e}")
            return []
        
        contents = repo.get_contents("")
        _logger.info(f"{contents=}")
        filenames = []
        for content_file in contents:
            if content_file.type == "dir":
                if content_file.name in ['.github','.gitignore','README.md']:
                    continue
                filenames.append(content_file.name)
        _logger.info(f"{filenames=}")
        return filenames

    def _get_github_response(self,filename,git_owner=None,git_repo=None):
        if not (git_owner and git_repo):
            git_owner = self.git_owner
            git_repo  = self.git_repo
        for branch in sorted(self._get_odoo_branches(git_owner,git_repo),key=float, reverse=True):
            branch_url = f"{GITHUB_RAW_URL}/{git_owner}/{git_repo}/{branch}"
            _logger.warning(f"get file---->   {branch_url}/{filename}")
            response = requests.get(f"{branch_url}/{filename}")
            if response.status_code == 200:
                return (response.status_code,branch,response)
        return (None,None,None)
        
#TODO Issues
#TODO Pull Requests
        

    

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
    
    def _get_github_response(self,filename,git_owner=None,git_repo=None):
        if not (git_owner or git_repo):
            git_owner = self.module_author
            git_repo  = self.git_repo   
        if not self.git_module:
            raise UserError(_("Git Module is missing"))
        (status_code,branch,response) = self.project_id._get_github_response(f"{self.git_module}/{filename}",git_owner,git_repo)
        if status_code == 200:
            self.write({'odoo_version': branch,})
            return (response, branch)
        return (None,None)

    def _get_github_file(self,filename,git_owner=None,git_repo=None):
        (response,branch) = self._get_github_response(filename,git_owner,git_repo)
        if response:
            return (response.text,branch)

    def _get_github_content(self,filename,git_owner=None,git_repo=None):
        (response,branch) = self._get_github_response(filename,git_owner,git_repo)
        if response:
            return (response.content,branch)

    def get_module_info(self):
        for task in self:
            task.load_manifest()
            task.load_banner()
            task.load_index()

    def load_manifest(self,git_owner=None,git_repo=None):
        # ~ https://pygithub.readthedocs.io/en/latest/examples/Repository.html
        # ~ https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
        if not (git_owner or git_repo):
            git_owner = self.module_author
            git_repo  = self.git_repo
        _logger.warning(f"wrong  --- {not (git_owner or git_repo)=} {git_owner=} {git_repo=}")
        for task in self:
            (manifest,branch) = task._get_github_file('__manifest__.py',git_owner,git_repo)
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
                if task.odoo_version != branch:
                    task.message_post(body=f"""
                        Information updated for {task.odoo_version=}
                        """)
            return branch
    def load_banner(self,git_owner=None,git_repo=None):
        if not (git_owner and git_repo):
            git_owner = self.module_author
            git_repo  = self.git_repo        
        branch = None
        for task in self:
            banner = task.attachment_ids.filtered(lambda a: a.name == 'banner.png')
            if not banner:
                (content,branch) = task._get_github_content('static/description/banner.png',git_owner,git_repo)
                if not content:
                    (content, branch) = task._get_github_content('static/description/icon.png',git_owner,git_repo)
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
        return branch

    def load_index(self,git_owner=None,git_repo=None):
        if not (git_owner and git_repo):
            git_owner = self.module_author
            git_repo  = self.git_repo
        for task in self:
            (index, branch) = task._get_github_file('static/description/index.html',git_owner,git_repo) 
            if index:
                task.module_website_desc = index
        return branch
