from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
from github import Github, Auth
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
        project = self.env['project.project'].browse(project_id)
        branches = project._get_odoo_branches(git_owner=author,git_repo=repo_name)
        for branch in branches:
            stage = self.env['project.task.type'].search([('project_ids','in',project_id),('name','=',branch)])
            if not stage:
                self.env['project.task.type'].create({
                    'project_ids': [(6,0,[project_id])],
                    'name': branch,
                    })

        for content_file in project._get_git_contents(git_owner=author,git_repo=repo_name):
            task = self.env['project.task'].search([('project_id','=',project_id),('git_module','=',content_file)])
            if task and not update_modules:
                continue 
            if not task:
                task = self.env['project.task'].create({
                    'name':content_file ,
                    'git_module': content_file, 
                    'git_repo': git_repo, 
                    'git_owner': git_owner,
                    'is_odoo_module': True,
                    'project_id': project.id})
            _logger.info(f"{content_file=}")  
            branch = task.load_manifest()
            _logger.info(f"{branch=}")  
            if task.odoo_version != branch:
                task.message_post(body=f"""
                        Information updated for {branch=}
                """)
            version_ids = self.env['project.task.type']
            version_ids = [stage for stage in self.env['project.task.type'].search([('project_ids','in',project_id),('name','in',branches)])]
            task.write({
                            'odoo_version': branch,
                            'module_branches': ','.join(branches),
                            'module_version_ids': [(6,0,[version.id for version in version_ids])],
                        })
            
            if stakeholder:
                task.module_stakeholder_ids = [(4,0,stakeholder.id)]
            task.load_banner()
            task.load_index()
                    
            # Put it on the highest branch stage
            version_id = self.env['project.task.type'].search([('project_ids','in',project_id),('name','=',branch)])
            task.stage_id = version_id.id
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
