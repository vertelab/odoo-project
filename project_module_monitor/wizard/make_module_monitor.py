from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import requests 

GITHUB_BASE_URL = 'https://api.github.com' 


#import dateutil.relativedelta as relativedelta
#from datetime import datetime

_logger = logging.getLogger(__name__)

  
class make_module_monitor(models.TransientModel):
    _name = "project.module.monitor.wizard"
    _description = "Load moduels from GitHub."

    module_author = fields.Char(string="Authour") # example vertel,oca
    git_repo = fields.Char(string="Git Repo", help="For example odoo-l10n_se") # example l10n_se
    git_module = fields.Char(string="Git Module", help="For example l10n_se_tax_report") # example l10n_se_tax_report
    
    module_stakeholder_ids = fields.Many2one('res.partner')# example SKF, Skogsstyrelsen, Dollarstore
    odoo_version = fields.Integer('Odoo Version', default=16)
    #(string="Module stakeholder", help="For example Vertel, OCA, ... and more ") # example...
    # ~ (comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))
    
    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))

    
    def load_modules(self):
        organization_repositories_url = f"{GITHUB_BASE_URL}/orgs/{self.module_author}/repos"
        response = requests.get(organization_repositories_url)
        if response.status_code == 200:
            repositories = response.json()
            raise UserWarning("%s" % repositories)
        else:
            raise UserWarning(f"Failed to retrieve repositories. Status code: {response.status_code}")


