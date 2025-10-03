# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = "project.task"
    
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
      
    equity_price_ids = fields.One2many(
        comodel_name='project.task.stock.price',
        inverse_name='task_id',
        string='Stock Transactions'
    )

    @api.depends('equity_price_ids', 'equity_price_ids.date')
    def _compute_latest_stock_price(self):
        for equity in self:
            transaction = self.search(
            [('task_id', '=', equity.id)],
            order='date desc',
            limit=1
                )
            if transaction:
                equity.price = transaction.price
            else:
                equity.price = 0.0

    equity_price = fields.Monetary(string="Price", currency_field='currency_id', compute='_compute_latest_stock_price',
        store=True)
        
    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        string='Currency', 
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )


class ProjectTaskStockPrice(models.Model):
    _name = 'project.task.equity.price'
    _description = 'Stock price transaction linked to task'

    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade')
    price = fields.Float(string='Stock Price', required=True)
    equity_symbol = fields.Char(string='Stock Symbol', related='task_id.equity_symbol')
    date = fields.Date(string='Transaction Date', default=fields.Date.context_today)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_equity_portfolio = fields.Boolean(string='Is Equity Portfolio')
    valuation_ids = fields.One2many(
        comodel_name='project.project.valuation',
        inverse_name='project_id',
        string='Daily Valuations'
    )

    @api.depends('valuation_ids', 'valuation_ids.date')
    def _compute_value(self):
        for portfolio in self:
            transaction = self.search(
            [('task_id', '=', equity.id)],
            order='date desc',
            limit=1
                )
            if transaction:
                equity.price = transaction.price
            else:
                equity.price = 0.0

    equity_value = fields.Monetary(string="Value", currency_field='currency_id', compute='_compute_value', store=True)
        
    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        string='Currency', 
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )

    

class ProjectProjectValuationRecord(models.Model):
    _name = 'project.project.valuation'
    _description = 'Daily valuation of project'

    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    date = fields.Date(string='Valuation Date', default=fields.Date.context_today, required=True)
    value = fields.Float(string='Valuation Value', required=True)

    @api.models
    def _compute_valuation(self):
        for portfolio in self.env['project.project'].search([('is_equity_portfolio','=',True)]):
            self.env['project.project.valuation'].create({
            'project_id': portfolio.id,
            'value': sum(portfolio.task_ids.mapped('price')),
            'date': fields.Date.context_today(self)
        })

