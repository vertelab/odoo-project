from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
from github import Github
import re
import base64

GITHUB_BASE_URL = 'https://api.github.com'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com'

#import dateutil.relativedelta as relativedelta
#from datetime import datetime

_logger = logging.getLogger(__name__)

#TODO  Add Odoo-core button
class GitRepo(models.TransientModel):
    _name = 'git.repos'
    _description = 'Git Repositories'

    name = fields.Char(string="Name")
    author = fields.Char(string="Author")

    def load_modules(self, author, repo_name,project_id,update_modules,stakeholder=None):
        # ~ https://pygithub.readthedocs.io/en/latest/examples/Repository.html
        # ~ https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
        g = Github()
        missing_modules = []
        try:
            # ~ repo = g.get_repo(f"self.module_author/odoo-l10n_se")
            # ~ raise UserWarning(f"{self.module_author}/{self.git_repo.name}")
            repo = g.get_repo(f"{author}/{repo_name}")
        except Exception as e:
            raise UserError(f"Could not read {author}/{repo_name} {e}")

        branches = [b.name for b in repo.get_branches() if re.match("^\d*[.]0$", b.name)]
        for branch in branches:
            stage = self.env['project.task.type'].search([('project_ids','in',project_id),('name','=',branch)])
            if not stage:
                self.env['project.task.type'].create({
                    'project_ids': [(6,0,[project_id])],
                    'name': branch,
                    })

        contents = repo.get_contents("")
        _logger.info(f"{contents=}")
        for content_file in contents:
            module_branch = {}
            if content_file.type == "dir":
                if content_file.name in ['.github','.gitignore','README.md']:
                    continue
                task = self.env['project.task'].search([('project_id','=',project_id),('git_module','=',content_file.name)])
                if task and not update_modules:
                    continue 
                    

                for b in branches:
                    # ~ self.message_box = f"{repo_name} {content_file.name} {b}"
                    _logger.info(f"{repo_name} {content_file.name} {b}")
                    branch_url = f"{GITHUB_RAW_URL}/{author}/{repo.name}/{b}/"
                    response = requests.get(f"{branch_url}/{content_file.name}/__manifest__.py")
                    if response.status_code == 200:
                        module_branch[b] = eval(response.text)
                    else:
                        missing_modules.append(f"{content_file.name} {b=}(no manifest)")
                if len(module_branch.keys()) > 0:
                    version_ids = self.env['project.task.type']
                    version_ids = [stage for stage in self.env['project.task.type'].search([('project_ids','in',project_id),('name','in',module_branch.keys())])]
                    
                    branch = sorted(module_branch.keys())[-1]
                    branch_url = f"{GITHUB_RAW_URL}/{author}/{repo.name}/{branch}/"
                    
                    #TODO Get module_website_desc  index.html
                    rec = {
                            'project_id': project_id,
                            'name': module_branch[branch].get('name'),
                            'git_module': content_file.name,
                            'module_author': author,
                            'git_repo': repo.name,
                            'odoo_version': branch,
                            'description': module_branch[branch].get('description',''),
                            'module_summary': module_branch[branch].get('summary',''),
                            'module_category': module_branch[branch].get('category',''),
                            'module_website': module_branch[branch].get('website',''),
                            'module_images': ','.join(module_branch[branch].get('images',[])),
                            'module_license': module_branch[branch].get('license',''),
                            'module_maintainer': module_branch[branch].get('maintainer',''),
                            'module_depends': ','.join(module_branch[branch].get('depends',[])),
                            'module_installable': module_branch[branch].get('installable',False),
                            'module_application': module_branch[branch].get('application',False),
                            'module_auto_install': module_branch[branch].get('auto_install',False),
                            'module_branches': ','.join(module_branch.keys()),
                            'module_version_ids': [(6,0,[version.id for version in version_ids])],
                        }

                    if not task:
                        task = self.env['project.task'].create(rec)
                    else:
                        task.write(rec)
                        task.message_post(body=f"""
                        Information updated for {branch=}
                        """)
                        if stakeholder:
                            task.stakeholder_ids = [(4,0,stakeholder.id)]
                    banner = task.attachment_ids.filtered(lambda a: a.name == 'banner.png')
                    if not banner:
                        response = requests.get(f"{branch_url}/{content_file.name}/static/description/banner.png")
                        
                        if not response.status_code == 200:
                            response = requests.get(f"{branch_url}/{content_file.name}/static/description/icon.png")
                        if response.status_code == 200:
                            banner = self.env["ir.attachment"].create(
                                    {
                                        "name": 'banner.png',
                                        "res_id": task.id,
                                        "res_model": str(task._name),
                                        "datas": base64.encodebytes(response.content),
                                    }
                                )
                            task.displayed_image_id = banner.id
                    response = requests.get(f"{branch_url}/{content_file.name}/static/description/index.html")
                    if response.status_code == 200:
                        task.module_website_desc = response.text
                    
                    # Put it on the highest branch stage
                    version_id = self.env['project.task.type'].search([('project_ids','in',project_id),('name','=',branch)])
                    task.stage_id = version_id.id
                else:
                    missing_modules.append(f"{content_file.name} (no branch)")
        return missing_modules



#TODO button for Add Repo at kanban view see crm_iap_lead
class ModuleMonitor(models.TransientModel):
    _name = "project.module.monitor.wizard"
    _description = "Load module from GitHub."

    module_author = fields.Char(string="Author",help="Coma separated string with autors")  # example vertel,oca
    author_lst    = fields.Char()

    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))
    git_repo_ids = fields.Many2many('git.repos', string="Git Repos",)
    # ~ git_repo_ids = fields.Many2many('git.repos', string="Git Repos", domain="[('author', 'in', author_lst)]")
    update_modules = fields.Boolean(string='Update module information')
    message_box = fields.Text(string='')

    @api.onchange('module_author')
    def _compute_git_repos(self):
        for rec in self:
            
            authors = rec.module_author.split(',') if rec.module_author else []
            rec.author_lst = "%s" % authors
            for author in authors:
                organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{author}/repos?per_page=100"
                # ~ if self.module_author == 'odoo':
                    # ~ organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{rec.module_author}/repos?per_page=100"
                    
                while organization_repositories_url:
                    response = requests.get(organization_repositories_url)

                    if response.status_code == 200:
                        repositories = response.json()
                        _logger.info(f"{len(repositories)=}")
                        for repo in repositories:
                            self._sync_git_repo(repo.get('name'), author)
                    organization_repositories_url = response.links.get('next', {}).get('url', None)

    def _sync_git_repo(self, repo_name, author):
        repo_id = self.env['git.repos'].search([('name', '=', repo_name), ('author', '=', author)], limit=1)
        if not repo_id:
            repo_id = self.env['git.repos'].create({'name': repo_name, 'author': author})
        return repo_id

    def load_modules(self):
        # ~ https://pygithub.readthedocs.io/en/latest/examples/Repository.html
        # ~ https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
        g = Github()
        missing_modules = []

        for rec in self:
            for author in rec.module_author.split(','):
                for git_repo in self.git_repo_ids:
                    res = self.env['git.repos'].load_modules(author,git_repo.name,rec.project_id.id,self.update_modules)
                    for m in res:
                        missing_modules.append(m)

        if len(missing_modules):
            self.message_box = "Failed modules: " + ','.join(missing_modules)
        return {
                "type": "ir.actions.act_window",
                "name": "Add Stakeholder",
                "res_model": "project.add.stakeholder.wizard",
                "res_id": self.id,
                "view_mode": "form",
                # ~ "domain": [("journal_id", "=", self.id)],
                "context": dict(self.env.context),
            }


            # ~ https://raw.githubusercontent.com/vertelab/odoo-l10n_se/14.0/l10n_se_nordea/__manifest__.py
