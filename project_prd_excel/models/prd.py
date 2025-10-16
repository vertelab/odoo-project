from datetime import datetime, timedelta 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging


import openpyxl
import base64
from io import BytesIO



_logger = logging.getLogger(__name__)


class ProductRequirementDocument(models.Model):
    _inherit = 'prd.document'
    
    def action_excel_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Load Requirements from Excel',
            'res_model': 'project_prd.excel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_week_template_id': self.env.context["default_week_template_id"]},
            #'domain': [('planning_id', '=', self.id)]
        }
        return action



class ExcelWizard(models.TransientModel):
    _name = 'prd.excel.wizard'
    _description = 'Load Requirements from Excel'

    file = fields.Binary(string="File", required=True)
 
 
    field_keys = [
        "csrd_id",
        "csrd_esrs",
        "csrd_dr",
        "csrd_paragraph",
        "csrd_related_ar",
        "csrd_name",
        "csrd_data_type",
        "csrd_conditional_or_alternative_dp",
        "csrd_may_v",
        "csrd_appendix_b",
        "csrd_appendix_c_less_then_750",
        "csrd_appendix_c_more_then_750",
        ]

    def import_excel(self):

            wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)))

            wslist = wb.sheetnames

            wslist.pop(0)

            for ws in wslist:

                activews = wb[ws]
                record = {}

                for row in range(3, activews.max_row + 1):
                    if activews.cell(row=row,column=1) != None:
                        for col in range(1, 13):
                            record_value = activews.cell(row=row, column=col).value
                            if record_value != None:
                                record_value = str(record_value).strip()
                                record_value = record_value.lower()
                                if record_value == "monerary":
                                    record_value = "monetary"
                                if "percentage" in record_value:
                                    record_value = record_value.replace("percentage", "percent")
                            record[self.field_keys[col-1]] = record_value
                        record['csrd_sheet_name'] = ws
                        self.create_record(record)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }


    def create_record(self,record):

            csrd_esrs_id = self.env["csrd.esrs"].search([("csrd_id", "=", record["csrd_id"])])

            if not csrd_esrs_id:

                self.env["csrd.esrs"].create(record)



