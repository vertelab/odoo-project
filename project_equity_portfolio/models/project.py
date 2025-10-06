# -*- coding: utf-8 -*-
from GoogleNews import GoogleNews
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import feedparser
import logging

_logger = logging.getLogger(__name__)

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_equity_portfolio = fields.Boolean(string='Is Equity Portfolio')

    @api.onchange('is_equity_portfolio')
    def _onchange_is_equity_portfolio(self):
        if self.is_equity_portfolio:
            self.type_ids = [(5, 0, 0)] 
            self.type_ids = [(6, 0, [self.env.ref('project_equity_portfolio.task_type_active'),self.env.ref('project_equity_portfolio.task_type_inactive')])]
        else:
            self.type_ids = [(5, 0, 0)]
            
    @api.depends('valuation_ids', 'valuation_ids.date')
    def _compute_value(self):
        for portfolio in self:
            latest_valuation = self.env['project.equity_valuation'].search(
                [('project_id', '=', portfolio.id)],
                order='date desc',
                limit=1
            )
            portfolio.equity_value = latest_valuation.value if latest_valuation else 0.0


    equity_research_lang = fields.Char(string='Lang', default='sv')
    equity_research_region = fields.Char(string='Region', default='SE')
    equity_research_period = fields.Char(string='Period', default='7d')
    equity_research_ids =  fields.One2many(
        comodel_name='project.equity_research',
        inverse_name='project_id',
        string='Articles'
    )
    equity_research_topic_ids =  fields.One2many(
        comodel_name='project.equity_research.topic',
        inverse_name='project_id',
        string='Topics'
    )
    
    def action_open_topics(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Topics',
            'res_model': 'project.equity_research.topic',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
    
    def action_open_research(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Research',
            'res_model': 'project.equity_research',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }
    
    
    equity_value = fields.Monetary(
        string="Value", 
        currency_field='currency_id', 
        compute='_compute_value', 
        store=True
    )

    equity_account = fields.Monetary(
        string="Account", 
        currency_field='currency_id', 
        compute='_compute_account', 
        store=True
    )
    @api.depends('transaction_ids', 'transaction_ids.date')
    def _compute_account(self):
        for portfolio in self:
            portfolio.equity_account = sum(portfolio.transaction_ids.mapped('equity_value'))

    equity_total = fields.Monetary(
        string="Total", 
        currency_field='currency_id', 
        compute='_compute_total', 
        store=True
    )
    @api.depends('transaction_ids', 'transaction_ids.date','valuation_ids', 'valuation_ids.date')
    def _compute_total(self):
        for portfolio in self:
            portfolio.equity_total = portfolio.equity_account + portfolio.equity_value

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )

    valuation_ids = fields.One2many(
        comodel_name='project.equity_valuation',
        inverse_name='project_id',
        string='Daily Valuations'
    )

    @api.depends('valuation_ids')
    def _compute_valuation_count(self):
        for record in self:
            record.valuation_count = len(record.valuation_ids)
    valuation_count = fields.Integer(
        string="Valuation Count",
        compute='_compute_valuation_count'
    )

    def action_open_valuations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Daily Valuations',
            'res_model': 'project.equity_valuation',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    transaction_ids = fields.One2many(
        comodel_name='project.equity_transaction',  # Use your actual model name
        inverse_name='project_id',
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
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_equity_transaction_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equity Transaction Wizard',
            'res_model': 'equity.transaction.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_project_id': self.id},
        }


    def equity_buy(self,equity_symbol,number,value,transaction_fee):
        for portfolio in self:
            equities = portfolio.task_ids.filtered(lambda e: e.equity_symbol == equity_symbol)
            if not equities:
                equity = self.env['project.task'].create({'name':equity_symbol,'equity_symbol':equity_symbol,'project_id': portfolio.id,'equity_number':number})
                price_transaction = self.env['project.task.equity_price'].create({'task_id':equity.id,'price': value / number})
            else:
                equity = equities[0]
            equity.equity_number += number
            if equity.stage_id != self.env.ref('project_equity_portfolio.task_type_active'):
                equity.stage_id = self.env.ref('project_equity_portfolio.task_type_active')
            transaction = self.env['project.equity_transaction'].create({
                'equity_value': value,
                'number':  number,
                'project_id': portfolio.id,
                'task_id': equity.id,
                'transaction_fee': transaction_fee,
                'transaction_type': 'buy'
            })
            
    def equity_sell(self,equity_symbol,number,value,transaction_fee):
        for portfolio in self:
            equities = portfolio.task_ids.filtered(lambda e: e.equity_symbol == equity_symbol)
            if not equities:
                raise UserError(f'Missing Equity Symbol {equity_symbol}')
            else:
                equity = equities[0]
            equity.equity_number -= number
            if equity.equity_number <= 0.0:
                equity.stage_id = self.env.ref('project_equity_portfolio.task_type_inactive')
            transaction = self.env['project.equity_transaction'].create({
                'equity_value': value*-1,
                'number':  number*-1,
                'project_id': portfolio.id,
                'task_id': equity.id,
                'transaction_fee': transaction_fee,
                'transaction_type': 'sell'
            })

    equity_research_rss = fields.Char(string='Rss-feed', default='https://www.placera.se/artiklar/rss.xml')
            
    def get_latest_rss(self):
        for portfolio in self:
            if portfolio.is_equity_portfolio:
                feed = feedparser.parse(portfolio.equity_research_rss)
                if not feed.bozo:
                    _logger.error(f"Read {len(feed.entries)=}")
                    
                    for entry in feed.entries:
                        # ~ _logger.warning(f"Feed: {entry.title} {entry.author}")
                        if self.env['project.equity_research'].search_count([('project_id','=',portfolio.id),('link','=',entry.link)])==0:
                            self.env['project.equity_research'].create({
                                'project_id': portfolio.id,
                                # ~ 'date': entry.pubDate,
                                'title': entry.title,
                                'desc': entry.description,
                                'link': entry.link,
                                'media': entry.author,
                                })
                else:
                    _logger.error(f"Could not read the feed {portfolio.equity_research_rss}")

    def get_latest_news(self):
        for portfolio in self:
            portfolio.get_latest_rss()
            if portfolio.is_equity_portfolio:
                for topic in portfolio.equity_research_topic_ids:
                    for item in topic.get_latest_news():
                        if item:
                            vals = {t: item.get(t, False) for t in ['title', 'media', 'date', 'desc', 'link', 'img']}
                            try:
                                valid_date = fields.Date.to_date(vals['date'])
                            except Exception:
                                valid_date = fields.Date.today()
                            vals['date'] = valid_date
                            vals['project_id'] = portfolio.id
                            vals['topic_id'] = topic.id
                            _logger.warn(vals)
                            if self.env['project.equity_research'].search_count([('project_id','=',portfolio.id),('link','=',vals['link'])])==0:
                                self.env['project.equity_research'].create(vals)
                        else:
                            _logger.warning('Item none')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Research',
            'res_model': 'project.equity_research',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self[0].id)],
            'context': {'default_project_id': self[0].id},
        }
        
            
class ProjectProjectValuationRecord(models.Model):
    _name = 'project.equity_valuation'
    _description = 'Daily valuation of project'

    date = fields.Date(string='Valuation Date', default=fields.Date.context_today, required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    value = fields.Float(string='Valuation Value', required=True)

    @api.model
    def _compute_valuation(self):
        for portfolio in self.env['project.project'].search([('is_equity_portfolio','=',True)]):
            self.env['project.equity_valuation'].create({
                'project_id': portfolio.id,
                'value': sum([task.price * task.number for task in portfolio.task_ids]),
                'date': fields.Date.context_today(self),
            })

class ProjectProjectTransaction(models.Model):
    _name = 'project.equity_transaction'
    _description = 'Selling and buying equity'

    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        string='Currency', 
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    date = fields.Date(string='Valuation Date', default=fields.Date.context_today, required=True)
    equity_value = fields.Monetary(string="Value", currency_field='currency_id')
    number = fields.Float(string='Number')
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    task_id = fields.Many2one('project.task', string='Task', required=True, ondelete='cascade')
    transaction_fee = fields.Monetary(string="Fee", currency_field='currency_id')
    transaction_type = fields.Selection(
        selection=[
            ('contribution','Cash Contribution'),
            ('withdrawal','Cash Withdrawal'),
            ('buy','Buy Equity'),
            ('sell','Sell Equity')
        ],
        string='Type'
    )

class ProjectEquityResearch(models.Model):
    _name = 'project.equity_research'
    _description = 'Research about equity portfolio'

    project_id = fields.Many2one('project.project', string='Portfolio', required=True, ondelete='cascade')
    desc = fields.Text(string='Research Summary', )
    title = fields.Char(string='Title', )
    link = fields.Char(string='Source URL', )
    img = fields.Char(string='Image', )
    media = fields.Char(string='Media', )
    search = fields.Char(string='Search', )
    topic_id = fields.Many2one(comodel_name='project.equity_research.topic',string="Topic",help="") # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegatefields.Char(string='Media', required=True)
    date = fields.Date(string='Research Date', default=fields.Date.context_today, )

class ProjectEquityResearchTopic(models.Model):
    _name = 'project.equity_research.topic'
    _description = 'Research about equity portfolio topic'

    project_id = fields.Many2one('project.project', string='Portfolio', required=True, ondelete='cascade')
    topic = fields.Text(string='Topic token', )
    name = fields.Char(string='Title', )
    sequence = fields.Integer(string='Sequence', )
    
    def get_latest_news(self):
        items = []
        for topic in self:
            googlenews = GoogleNews(lang=topic.project_id.equity_research_lang, 
                                    region=topic.project_id.equity_research_region, 
                                    period=topic.project_id.equity_research_period)
            googlenews.set_topic(topic.topic)
            news = googlenews.get_news()
            if news:
                items.extend(googlenews.get_news())
        return items
        
        # ~ topic ekonomi CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FuTjJHZ0pUUlNnQVAB
        # topic lokalt CAAqHAgKIhZDQklTQ2pvSWJHOWpZV3hmZGpJb0FBUAE/sections/CAQiW0NCSVNQam9JYkc5allXeGZkakpDRUd4dlkyRnNYM1l5WDNObFkzUnBiMjV5RHhJTkwyY3ZNVEZ3ZUhseE5IZHFNbm9QQ2cwdlp5OHhNWEI0ZVhFMGQyb3lLQUEqNggAKjIICiIsQ0JJU0d6b0liRzlqWVd4ZmRqSjZEd29OTDJjdk1URndlSGx4TkhkcU1pZ0FQAVAB
        # topic vetenskap/teknik CAAqKAgKIiJDQkFTRXdvSkwyMHZNR1ptZHpWbUVnSnpkaG9DVTBVb0FBUAE
        # topic nöje CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FuTjJHZ0pUUlNnQVAB
        # topic hälsa CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FuTjJLQUFQAQ
        # set_topic
        
