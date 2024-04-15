from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import requests
from github import Github
import re

GITHUB_BASE_URL = 'https://api.github.com' 


#import dateutil.relativedelta as relativedelta
#from datetime import datetime

_logger = logging.getLogger(__name__)

  
class make_module_monitor(models.TransientModel):
    _name = "project.module.monitor.wizard"
    _description = "Load moduels from GitHub."

    module_author = fields.Char(string="Authour") # example vertel,oca
    
    def _get_git_repo(self):
        organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{self.module_author}/repos"
        organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/vertelab/repos"
        response = requests.get(organization_repositories_url)
        # ~ raise UserWarning("%s" % [(r['name'],r['full_name']) for r in response.json()])
        if response.status_code == 200:
            repositories = response.json()
            return [(repo['name'],repo['full_name']) for repo in repositories]
        else:
            return [(None,None)]
    git_repo = fields.Selection(_get_git_repo,string="Git Repo", help="For example odoo-l10n_se") # example l10n_se
    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))

    
    

    @api.onchange('Xmodule_author')
    def _change_module_autor(self):
        organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{self.module_author}/repos"
        response = requests.get(organization_repositories_url)
        if response.status_code == 200:
            repositories = response.json()
            return [(repo['name'],repo['name']) for repo in repositories] 
        else:
            return [(None,None)]
    
    def load_modules(self):
        g = Github()
        try:
            repo = g.get_repo(f"self.module_author/self.git_repo")
        except Exception as e:
            # ~ raise UserWarning(f"Could not read {self.module_author}/{self.git_repo} {e}")
            repo = g.get_repo(f"self.module_author/odoo-l10n_se")
        branches = [b.name for b in repo.get_branches() if re.match("^\d*[.]0$",b.name)] 
        
        raise UserWarning("%s" % branches)
        # ~ https://raw.githubusercontent.com/vertelab/odoo-l10n_se/14.0/l10n_se_nordea/__manifest__.py
        
        
        organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{self.module_author}/repos"
        response = requests.get(organization_repositories_url)
        if response.status_code == 200:
            repositories = response.json()
            raise UserWarning("%s" % repositories)
        else:
            raise UserWarning(f"Failed to retrieve repositories. Status code: {response.status_code}")


