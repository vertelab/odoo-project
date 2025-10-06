# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = "project.task"
    
    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        string='Currency', 
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    
    is_equity_portfolio = fields.Boolean(string='Is Equity Portfolio',related="project_id.is_equity_portfolio")
    equity_number = fields.Float(string='Number',default=1.0)
    equity_price = fields.Monetary(
        string="Price", 
        currency_field='currency_id', 
        compute='_compute_latest_stock_price',
        store=True
    )
    equity_price_count = fields.Integer(string='Equity Price Count', compute='_compute_equity_price_count')
    equity_price_ids = fields.One2many(
        comodel_name='project.task.equity_price',
        inverse_name='task_id',
        string='Equity Prices'
    )
    equity_research_count = fields.Integer(string='Equity Research Count', compute='_compute_equity_research_count')
    equity_research_ids = fields.One2many(
        comodel_name='project.task.equity_research',
        inverse_name='task_id',
        string='Equity Research'
    )
    equity_symbol = fields.Char(string='Stock Symbol', required=True)
    equity_type = fields.Selection(
        selection=[
            ('stock', 'Stock'),
            ('fund', 'Fund'),
            ('interest_fund', 'Interest Fund'),
            ('obligation', 'Obligation'),
            ('derivative', 'Derivat'),
            ('future', 'Future'),
        ],
        string='Type of financial instrument'
    )
    equity_value = fields.Monetary(
        string="Value", 
        currency_field='currency_id', 
        compute='_compute_latest_stock_price',
        store=True
    )

    @api.depends('equity_price_ids', 'equity_price_ids.date')
    def _compute_latest_stock_price(self):
        for equity in self:
            transaction = self.env['project.task.equity_price'].search(
                [('task_id', '=', equity.id)],
                order='date desc',
                limit=1
            )
            if transaction:
                equity.equity_price = transaction.price
                equity.equity_value = equity.equity_number * transaction.price
            else:
                equity.equity_price = 0.0

    @api.depends('equity_price_ids')
    def _compute_equity_price_count(self):
        for task in self:
            task.equity_price_count = len(task.equity_price_ids)

    @api.depends('equity_research_ids')
    def _compute_equity_research_count(self):
        for task in self:
            task.equity_research_count = len(task.equity_research_ids)

    def action_open_equity_prices(self):
        self.ensure_one()
        return {
            'name': 'Equity Prices',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.equity_price',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
            'target': 'current',
        }

    def action_open_equity_research(self):
        self.ensure_one()
        return {
            'name': 'Equity Research',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task.equity_research',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
            'target': 'current',
        }


    transaction_ids = fields.One2many(
        comodel_name='project.equity_transaction',
        inverse_name='task_id',
        string='Transactions'
    )


    @api.depends('transaction_ids')
    def _compute_transaction_count(self):
        for record in self:
            record.transaction_count = len(record.transaction_ids)
    transaction_count = fields.Integer(
        string="Transaction Count",
        compute='_compute_transaction_count'
    )

    def action_open_transactions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transactions',
            'res_model': 'project.equity_transaction',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
        }

class ProjectTaskStockPrice(models.Model):
    _name = 'project.task.equity_price'
    _description = 'Stock price transaction linked to task'

    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade')
    price = fields.Float(string='Stock Price', required=True)
    equity_symbol = fields.Char(string='Stock Symbol', related='task_id.equity_symbol')
    date = fields.Date(string='Transaction Date', default=fields.Date.context_today)

class ProjectTaskEquityResearch(models.Model):
    _name = 'project.task.equity_research'
    _description = 'Research about equity'

    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade')
    equity_symbol = fields.Char(string='Stock Symbol', related='task_id.equity_symbol')
    research_text = fields.Text(string='Research Summary', required=True)
    source_url = fields.Char(string='Source URL', required=True)
    date = fields.Date(string='Research Date', default=fields.Date.context_today, required=True)
