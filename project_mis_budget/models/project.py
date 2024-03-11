from odoo import models, fields, api, _
import ast


class Project(models.Model):
    _inherit = "project.project"

    is_budget = fields.Boolean(string='Project Budget', help="Using project to construct a new complex MIS-budget")
    budget_id = fields.Many2one(comodel_name='mis.budget.by.account', string="Budget",
                                help="Budget tied to this project")

    is_kpi_budget = fields.Boolean(string='KPI Budget',
                                   help="Using KPI Budget on project to construct a new complex MIS-budget")
    kpi_budget_id = fields.Many2one(comodel_name='mis.budget', string="KPI Budget",
                                    help="KPI Budget tied to this project")

    def view_budget_by_account(self):
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id(
            'project_mis_budget.project_mis_budget_by_account_act_window')
        action['display_name'] = _("%(name)s", name=self.name)
        context = action['context'].replace('active_id', str(self.id))
        context = ast.literal_eval(context)
        action['context'] = context
        return action

    def view_budget_by_kpi(self):
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id(
            'project_mis_budget.project_mis_budget_act_window')
        action['name'] = _("%(name)s", name=self.name)
        context = action['context'].replace('active_id', str(self.id))
        context = ast.literal_eval(context)
        action['context'] = context
        return action


class Task(models.Model):
    _inherit = "project.task"

    is_budget = fields.Boolean(string="Is Budget", related="project_id.is_budget", store=True)
    budget_id = fields.Many2one(related="project_id.budget_id",
                                string="Budget", related_sudo=False, store=True)
    budget_item_id = fields.Many2one(
        comodel_name='mis.budget.by.account.item',
        string="Budget Item", help="Budget Item tied to this task",
        domain="[('budget_id', '=', budget_id)]",
    )

    is_kpi_budget = fields.Boolean(string="KPI Budget", related="project_id.is_kpi_budget", store=True)
    kpi_budget_id = fields.Many2one(related="project_id.kpi_budget_id",
                                    string="KPI Budget", related_sudo=False, store=True)
    kpi_budget_item_id = fields.Many2one(
        comodel_name='mis.budget.item',
        string="KPI Budget Item", help="KPI Budget Item tied to this task",
        domain="[('budget_id', '=', kpi_budget_id)]",
    )

    def view_budget_by_account_item(self):
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id(
            'project_mis_budget.project_mis_budget_by_account_item_act_window')
        action['display_name'] = _("%(name)s", name=self.name)
        context = action['context'].replace('active_id', str(self.id))
        context = ast.literal_eval(context)
        action['context'] = context
        return action

    def view_budget_by_kpi_item(self):
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id(
            'project_mis_budget.project_mis_budget_item_act_window')
        action['display_name'] = _("%(name)s", name=self.name)
        context = action['context'].replace('active_id', str(self.id))
        context = ast.literal_eval(context)
        action['context'] = context
        return action
