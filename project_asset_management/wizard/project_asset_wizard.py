from odoo import models, fields, api, _


class Project(models.TransientModel):
    _name = "project.asset.wizard"
    _description = "Project Asset Wizard"

    project_id = fields.Many2one('project.project', string="Project")
    profile_id = fields.Many2one('account.asset.profile', string="Profile")
    start_date = fields.Date(string="Start Date")

    purchase_value = fields.Monetary(
        required=True,
        help="This amount represent the initial value of the asset."
             "\nThe Depreciation Base is calculated as follows:"
             "\nPurchase Value - Salvage Value.")

    method_time = fields.Selection(
        [("year", _("Number of Years or end date")), ("number", _("Number of Depreciation"))],
        string="Time Method",
        required=True,
        default="year",
        help="Choose the method to use to compute the dates and "
             "number of depreciation lines.\n"
             "  * Number of Years: Specify the number of years "
             "for the depreciation.\n"
             "  * Number of Depreciation: Fix the number of "
             "depreciation lines and the time between 2 depreciation.\n",
    )
    method_period = fields.Selection(
        [("month", _("Month")), ("quarter", _("Quarter")), ("year", _("Year"))],
        string="Period Length",
        required=True,
        default="year",
        help="Period length for the depreciation accounting entries",
    )
    method = fields.Selection(
        [
            ("linear", _("Linear")),
            ("linear-limit", _("Linear up to Salvage Value")),
            ("degressive", _("Degressive")),
            ("degr-linear", _("Degressive-Linear")),
            ("degr-limit", _("Degressive  up to Salvage Value")),
        ],
        string="Computation Method",
        required=True,
        help="Choose the method to use to compute the depreciation lines.\n"
             "  * Linear: Calculated on basis of: "
             "Depreciation Base / Number of Depreciation. "
             "Depreciation Base = Purchase Value - Salvage Value.\n"
             "  * Linear-Limit: Linear up to Salvage Value. "
             "Depreciation Base = Purchase Value.\n"
             "  * Degressive: Calculated on basis of: "
             "Residual Value * Degressive Factor.\n"
             "  * Degressive-Linear (only for Time Method = Year): "
             "Degressive becomes linear when the annual linear "
             "depreciation exceeds the annual degressive depreciation.\n"
             "   * Degressive-Limit: Degressive up to Salvage Value. "
             "The Depreciation Base is equal to the asset value.",
        default="linear",
    )

    @api.model
    def _default_company_id(self):
        return self.env.company

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self._default_company_id(),
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        store=True,
    )

    def _create_asset(self):
        account_asset_id = self.env['account.asset'].create({
            'name': self.project_id.name,
            'profile_id': self.profile_id.id,
            'date_start': self.start_date,
            'purchase_value': self.purchase_value,
            'method': self.method,
            'method_time': self.method_time,
            'method_period': self.method_period,
        })
        return account_asset_id

    def action_create_open_asset(self):
        account_asset_id = self._create_asset()
        return {
            'name': _('Asset'),
            'view_mode': 'form',
            'res_model': 'account.asset',
            'res_id': account_asset_id.id,
            'type': 'ir.actions.act_window',
            # 'context': self._context
        }

    def action_create_asset(self):
        return self._create_asset()
