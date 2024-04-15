from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import requests
import re

from openpyxl import load_workbook
from xlrd import open_workbook, XLRDError
from xlrd.book import Book
from xlrd.sheet import Sheet


_logger = logging.getLogger(__name__)

class add_stakeholder(models.TransientModel):
    _name = "project.add.stakeholder.wizard"
    _description = "Add stakeholders to Projects."

    partner_id = fields.Many2one('res.partner')# example SKF, Skogsstyrelsen, Dollarstore
    stakeholder_file = fields.Binary(string='Stakeholder modules', help='Excel file exported from an Odoo instance.')
    
    project_id = fields.Many2one(comodel_name="project.project", default=lambda b: b.env.context.get('active_id'))

    def load_file(self):
        module_file = open_workbook(file_contents=self.stakeholder_file).sheet_by_index(0)
        author_pos = module_pos = 0
        for i in range(1,20):
            if module_file.cell(0,i).value in ['Författare','Author']:
                author_pos = i
            if module_file.cell(0,i).value in ['Tekniskt namn','Technical Name']:
                module_pos = i
        for row in range(1,module_file.nrows):
            author_name = module_file.cell(row,author_pos).value
            module_name = module_file.cell(row,module_pos).value
            # if we have the module (project.task) add stakeholder
            # if we dont have the module add to list of missing modules
            # What will we do with Odoo Core?
        
