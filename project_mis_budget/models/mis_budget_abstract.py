# Copyright 2024 Vertel AB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MisBudgetAbstract(models.AbstractModel):
    _inherit = "mis.budget.abstract"

    task_ids = fields.One2many(comodel_name='project.task', inverse_name="budget_item_id", string="Task",
                               help="Budgeting task for this item", )
    project_id = fields.Many2one(comodel_name='project.project', string="Project", help="Budgeting project", )
