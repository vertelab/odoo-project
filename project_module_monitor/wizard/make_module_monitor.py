from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import requests
from github import Github
import re

GITHUB_BASE_URL = 'https://api.github.com' 
GITHUB_RAW_URL  = 'https://raw.githubusercontent.com' 


#import dateutil.relativedelta as relativedelta
#from datetime import datetime

_logger = logging.getLogger(__name__)

class GitRepo(models.TransientModel):
      _name = 'git.repos'

      name = fields.Char(string="Name")
      author = fields.Char(string="Author")


class make_module_monitor(models.TransientModel):
    _name = "project.module.monitor.wizard"
    _description = "Load moduels from GitHub."

    module_author = fields.Char(string="Authour") # example vertel,oca

    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))
    git_repo = fields.Many2one('git.repos', string="Git Repos", domain="[('author', '=', module_author)]")

    @api.onchange('module_author')
    def _compute_git_repos(self):
        for rec in self:
            organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{rec.module_author}/repos?per_page=100"
            while organization_repositories_url:
                response = requests.get(organization_repositories_url)

                if response.status_code == 200:
                   repositories = response.json()
                   _logger.info(f"{len(repositories)=}")
               	   for repo in repositories:
                       self._sync_git_repo(repo.get('name'), rec.module_author)
                organization_repositories_url = response.links.get('next', {}).get('url', None)

    def _sync_git_repo(self, repo_name, author):
        repo_id = self.env['git.repos'].search([('name', '=', repo_name), ('author', '=', author)], limit=1)
        if not repo_id:
           repo_id = self.env['git.repos'].create({'name': repo_name, 'author': author})
        return repo_id



    def load_modules(self):
        # ~ https://pygithub.readthedocs.io/en/latest/examples/Repository.html
        g = Github()
        try:
            repo = g.get_repo(f"self.module_author/odoo-l10n_se")
            # ~ repo = g.get_repo(f"{self.module_author}/{self.git_repo}")
        except Exception as e:
            # ~ raise UserWarning(f"Could not read {self.module_author}/{self.git_repo} {e}")
            repo = g.get_repo(f"self.module_author/odoo-l10n_se")
        branches = [b.name for b in repo.get_branches() if re.match("^\d*[.]0$",b.name)] 

        contents = repo.get_contents("")

        for content_file in contents:
            module_branch = {}
            if content_file.type == "dir":
                for b in branches:
                    branch_url = f"{GITHUB_RAW_URL}/{self.module_author}/{repo.name}/{b}/"
                    response = requests.get(f"{branch_url}/{content_file.name}/__manifest__.py")
                    if response.status_code == 200:
                        module_branch[b] = eval(response.text)
                if len(module_branch.keys())>0:
                    raise UserWarning("%s" % module_branch)
                    # Create project.task
                    # add list of branches
                    # Put it on the highest branch stage
                    # What info from manifest are we interersted in?
            # ~ https://raw.githubusercontent.com/vertelab/odoo-l10n_se/14.0/l10n_se_nordea/__manifest__.py
