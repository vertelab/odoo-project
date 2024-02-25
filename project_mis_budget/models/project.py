from odoo import models, fields, api, _


class Project(models.Model):
    _inherit = "project.project"

    is_budget = fields.Boolean(string='Budget project',help="Using project to construct a new complex MIS-budget")
    budget_id = fields.Many2one(comodel_name='mis.budget.by.account',string="Budget",help="Budget tied to this project") 
    
class Task(models.Model):
    _inherit = "project.task"

    is_budget = fields.Boolean(string="Is Budget",related="project_id.is_budget") 
    budget_id = fields.Many2one(comodel_name='mis.budget.by.account',string="Budget",related="project_id.budget_id") 
    budget_item_id = fields.Many2one(comodel_name='mis.budget.by.account.item',
                    string="Budget Item",help="Budget Item tied to this task",
                    # ~ domain=[('budget_id','=',budget_id)],
                    )
