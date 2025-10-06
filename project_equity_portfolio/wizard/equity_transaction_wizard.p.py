from odoo import models, fields, api
from odoo.exceptions import UserError

class EquityTransactionWizard(models.TransientModel):
    _name = 'equity.transaction.wizard'
    _description = 'Equity Transaction Wizard'

    transaction_type = fields.Selection([
        ('contribution','Cash Contribution'),
        ('buy', 'Buy Equity'),
        ('sell', 'Sell Equity'),
        ('withdrawal', 'Cash Withdrawal'),
    ], string='Transaction Type', required=True, default='buy')

    project_id = fields.Many2one('project.project', string='Project', required=True)
    equity_symbol = fields.Char(string='Symbol', size=64, trim=True,)
    task_id = fields.Many2one('project.task', string='Task', required=False)
    number = fields.Float(string='Number', required=False)
    equity_value = fields.Monetary(string='Equity Value', currency_field='currency_id', required=False)
    transaction_fee = fields.Monetary(string='Transaction Fee', currency_field='currency_id', required=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id.id, )
    date = fields.Date(string='Transaction Date', default=fields.Date.context_today, required=True)

    @api.onchange('project_id')
    def _onchange_project_set_default_task(self):
        if self.project_id:
            # Optionally, set task_id to first task of project by default
            tasks = self.env['project.task'].search([('project_id', '=', self.project_id.id)])
            self.task_id = tasks and tasks[0] or False

    def action_confirm(self):
        self.ensure_one()

        if self.transaction_type in ['sell'] and not self.task_id:
            raise UserError("You must select a Task when buying or selling equity.")


        vals = {
            'transaction_type': self.transaction_type,
            'project_id': self.project_id.id,
            'task_id': self.task_id.id if self.task_id else False,
            'number': self.number or 0.0,
            'equity_value': self.equity_value or 0.0,
            'transaction_fee': self.transaction_fee or 0.0,
            'currency_id': self.currency_id.id,
            'date': self.date,
        }

        # For sell and withdrawal, invert the number and value appropriately
        if self.transaction_type == 'sell':
            self.project_id.equity_sell(self.equity_symbol,self.number,self.equity_value,self.transaction_fee)
        elif self.transaction_type == 'buy':
            self.project_id.equity_buy(self.equity_symbol,self.number,self.equity_value,self.transaction_fee)
        elif self.transaction_type == 'withdrawal':
            # For cash withdrawal, task and equity may be irrelevant, number & equity_value denote cash flow
            vals['number'] = 0.0  # or some suitable default
            vals['equity_value'] = -abs(vals['equity_value'])
            self.env['project.equity_transaction'].create(vals)
        elif self.transaction_type == 'contribution':
            vals['number'] = 0.0  # or some suitable default
            vals['equity_value'] = -abs(vals['equity_value'])
            self.env['project.equity_transaction'].create(vals)

        return {'type': 'ir.actions.act_window_close'}
