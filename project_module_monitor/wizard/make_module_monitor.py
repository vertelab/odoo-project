from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
#import dateutil.relativedelta as relativedelta
#from datetime import datetime

_logger = logging.getLogger(__name__)

  
class make_module_monitor(models.TransientModel):
    _name = "project.module.monitor.wizard"
    _description = "Load moduels from GitHub."

    module_author = fields.Char(string="Authour") # example vertel,oca
    git_repo = fields.Char(string="Git Repo", help="For example l10n_se") # example l10n_se
    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))

    
    def load_modules(self):
        pass


