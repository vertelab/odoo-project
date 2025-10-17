from datetime import datetime, timedelta 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging


import openpyxl
import base64
from io import BytesIO
import re



_logger = logging.getLogger(__name__)


class ProductRequirementDocument(models.Model):
    _inherit = 'prd.document'
    
    def action_excel_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Load Requirements from Excel',
            'res_model': 'prd.excel.wizard',
            'view_mode': 'form',
            'target': 'new',
            # ~ 'context': {'default_week_template_id': self.env.context["default_week_template_id"]},
        }
        return action



class ExcelWizard(models.TransientModel):
    _name = 'prd.excel.wizard'
    _description = 'Load Requirements from Excel'

    file = fields.Binary(string="File", required=True)
 
 
 
 

    def import_excel(self):
        """
        Läser en excel-fil (kravspecifikation) och skapar krav i prd.requirement.
        """
        try:
            wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)),data_only=True)
            # ~ wb = openpyxl.load_workbook(self.file, data_only=True)
        except Exception as e:
            raise UserError(_("Kunde inte läsa Excel-filen: %s") % e)

        requirement_model = self.env['prd.requirement']
        created_count = 0

        prd_id =   self.env.context['active_id']

        # Gå igenom varje blad i boken
        for sheet in wb.worksheets:
            _logger.warning(f"{sheet=}")
            current_page = sheet.title.strip()
            for row in sheet.iter_rows(values_only=True):
                if not row or not row[0]:
                    continue

                first_cell = str(row[0]).strip()
                _logger.warning(f"{row=} {first_cell=}")
                # Identifiera kravnummer (1.1, 2.1.5 etc.)
                
                if value and any(c.isdigit() for c in first_cell):
                # ~ if re.match(r'^\d+(\.\d+)*$', first_cell) or re.match(r'^\d+$', first_cell):
                    no = first_cell
                    name = (str(row[1]).strip() if len(row) > 1 and row[1] else None)
                    desc = (str(row[2]).strip() if len(row) > 2 and row[2] else name)
                    category = (str(row[3]).strip() if len(row) > 3 and row[3] else None)
                    priority_cell = " ".join(map(str, row)).lower()
                    # Bedöm prioritet
                    if "ska" in priority_cell:
                        priority = 'must'
                    elif "bör" in priority_cell or "br" in priority_cell:
                        priority = 'should'
                    elif "could" in priority_cell:
                        priority = 'could'
                    else:
                        priority = 'must'

                    # Skapa requirement-posten
                    values = {
                        'no': no,
                        'name': name or desc or "Unnamed Requirement",
                        'description': desc or '',
                        'category': category or '',
                        'page': current_page,
                        'priority': priority,
                        'prd_id': prd_id,
                        'req_type': 'func',  # kan utökas vid behov
                    }
                    _logger.warning(f"{values=}")
                    
                    requirement_model.create({
                        'no': no,
                        'name': name or desc or "Unnamed Requirement",
                        'description': desc or '',
                        'category': category or '',
                        'page': current_page,
                        'priority': priority,
                        'prd_id': prd_id,
                        'req_type': 'func',  # kan utökas vid behov
                    })
                    created_count += 1
                    break
        return 

    def Ximport_excel(self):

            wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)))
            
            # ~ raise UserError(f"{wb.sheetnames=}")
            for ws in wb.sheetnames:
                activews = wb[ws]
                record = {}                
                for row in range(1, activews.max_row + 1):
                    value = activews.cell(row=row,column=1).value
                    if value and any(c.isdigit() for c in str(value)): # Has numbers
                        record = {
                            'page': ws,
                            'no': activews.cell(row=row,column=1),
                             'category':  activews.cell(row=row,column=2).value if len(activews.cell(row=row,column=2).value) < 25 else '',
                             'name': activews.cell(row=row,column=2) if len(activews.cell(row=row,column=2).value) > 25 else activews.cell(row=row,column=3).value ,
                            'prd_id': self.env.context['active_id'],
                        
                        }
                        self.env['prd.requirement'].create(record)

                    # ~ if activews.cell(row=row,column=1) != None:
                        # ~ for col in range(1, 13):
                            # ~ record_value = activews.cell(row=row, column=col).value
                            # ~ if record_value != None:
                                # ~ record_value = str(record_value).strip()
                                # ~ record_value = record_value.lower()
                                # ~ if record_value == "monerary":
                                    # ~ record_value = "monetary"
                                # ~ if "percentage" in record_value:
                                    # ~ record_value = record_value.replace("percentage", "percent")
                            # ~ record[self.field_keys[col-1]] = record_value
                        # ~ record['csrd_sheet_name'] = ws
                        # ~ self.create_record(record)
            # ~ return {
                # ~ 'type': 'ir.actions.client',
                # ~ 'tag': 'reload',
            # ~ }


    def create_record(self,record):

            csrd_esrs_id = self.env["csrd.esrs"].search([("csrd_id", "=", record["csrd_id"])])

            if not csrd_esrs_id:

                self.env["csrd.esrs"].create(record)



