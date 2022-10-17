from odoo import models, fields, api, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    date_start_invoice_timesheet = fields.Date(
        string='Start Date',
        help="Only timesheets not yet invoiced (and validated, if applicable) from this period will be invoiced. "
             "If the period is not indicated, all timesheets not yet invoiced (and validated, if applicable) will "
             "be invoiced without distinction.", required=True)
    date_end_invoice_timesheet = fields.Date(
        string='End Date',
        help="Only timesheets not yet invoiced (and validated, if applicable) from this period will be invoiced. "
             "If the period is not indicated, all timesheets not yet invoiced (and validated, if applicable) will "
             "be invoiced without distinction.", required=True)
