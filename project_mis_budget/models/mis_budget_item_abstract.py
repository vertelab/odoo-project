# Copyright 2024- Vertel AB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MisBudgetItemAbstract(models.AbstractModel):
    _inherit = "mis.budget.item.abstract"

    task_id = fields.Many2one(comodel_name='project.task',string="Task",help="Budgeting task for this item",ondelete="cascade") 
    project_id = fields.Many2one(comodel_name='project.project',string="Project",help="Budgeting project",related="budget_id.project_id")
