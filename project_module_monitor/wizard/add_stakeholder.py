from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
import re

from openpyxl import load_workbook
from xlrd import open_workbook, XLRDError
from xlrd.book import Book
from xlrd.sheet import Sheet
import base64
from io import BytesIO


_logger = logging.getLogger(__name__)

class add_stakeholder(models.TransientModel):
    _name = "project.add.stakeholder.wizard"
    _description = "Add stakeholders to Projects."

    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner", help="Product owner / customer") # example SKF, Skogsstyrelsen, Dollarstore
    stakeholder_file = fields.Binary(string='Stakeholder modules', help='Excel file exported from an Odoo instance.')
    exclude_odoosa = fields.Boolean(string='Exclude Odoo SA', help='Dont try to check Odoo Core modules.')
    
    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))

    def load_file(self):
        #raise Warning(f"{self.stakeholder_file=}")
        module_file = load_workbook(filename=BytesIO(base64.b64decode(self.stakeholder_file))).active
        author_pos = module_pos = 1
        for i in range(1,20):
            if module_file.cell(1,i).value in ['Författare','Author']:
                author_pos = i
            if module_file.cell(1,i).value in ['Tekniskt namn','Technical Name']:
                module_pos = i
        # ~ raise Warning(f"{author_pos=} {module_pos=}")

        failed_modules = []
        for row in range(2,len(tuple(module_file.rows))):
            author_name = module_file.cell(row,author_pos).value
            module_name = module_file.cell(row,module_pos).value
            if self.exclude_odoosa and author_name in ["Odoo S.A.","Odoo SA"]:
                continue
            # if we have the module (project.task) add stakeholder
            module=self.env['project.task'].search([('project_id', '=', self.project_id.id), ('name', '=', module_name)]) # git_module 
            if len(module)==0:
                failed_modules.append((module_name,author_name))
                # ~ raise Warning(f"{module_name=} {module_pos=}")
            else:
                module.module_stakeholder_ids=[(6,0,[self.partner_id.id])]
                module.git_module_ids=[(6,0,[self.module_name.id])]
                
        if len(failed_modules) > 0:
            raise UserError(f"{failed_modules=}")   
            # git_module i stället för name
            
            
            
            
            
            # if we dont have the module add to list of missing modules
            # What will we do with Odoo Core?
