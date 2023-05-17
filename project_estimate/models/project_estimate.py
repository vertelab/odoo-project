from odoo import models, fields, api, _


class ProjectEstimate(models.Model):
    _name = "project.estimate"
    _description = "Project Estimate Analysis"

    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string="State", default="draft")
    line_ids = fields.One2many("project.estimate.line", "project_estimate_id", string="Line Items",
                               domain=([('parent_id', '=', False)]))
    currency_id = fields.Many2one("res.currency", string="Currency")

    unbuild_line_ids = fields.One2many("unbuild.estimate.line", "project_estimate_id", string="Unbuild Items")

    @api.depends("line_ids.sub_total")
    def _compute_expenses(self):
        for rec in self:
            rec.estimated_expenses = sum(
                rec.line_ids.filtered(lambda item: item.sub_total < 0).mapped("sub_total")
            )
            rec.estimated_income = sum(
                rec.line_ids.filtered(lambda item: item.sub_total > 0).mapped("sub_total")
            )

    estimated_expenses = fields.Monetary(string="Estimated Expenses", compute=_compute_expenses)
    estimated_income = fields.Monetary(string="Estimated Income")

    @api.depends("estimated_expenses", "estimated_income")
    def _compute_revenue_percentage(self):
        for rec in self:
            rec.estimated_revenue_percentage = ((rec.estimated_income + rec.estimated_expenses) / rec.estimated_income) * 100

    estimated_revenue_percentage = fields.Float(string="Revenue (%)", compute=_compute_revenue_percentage)

    def preview_sale_order(self):
        pass

    def action_view_invoice(self):
        invoice_view = self.env.ref('account.view_in_invoice_tree')
        return {
            'name': _('Invoices'),
            'domain': [("project_id", "=", self.project_id.id)],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': invoice_view.id,
            'views': [(invoice_view.id, 'tree'), (False, 'form')],
            'view_mode': 'tree,form',
        }

    def action_view_project(self):
        return {
            'name': _('Projects'),
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'views': [(False, 'form')],
            'view_mode': 'form',
            'res_id': self.project_id.id
        }

    def action_sale_order(self):
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'views': [(False, 'form')],
            'view_mode': 'form',
            'res_id': self.project_id.sale_order_id.id
        }

    def action_receive_shipment(self):
        picking_view = self.env.ref('stock.vpicktree')
        return {
            'name': _('Incoming Shipments'),
            'domain': [("project_id", "=", self.project_id.id)],
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_id': picking_view.id,
            'views': [(picking_view.id, 'tree'), (False, 'form')],
            'view_mode': 'tree,form',
        }

    def action_unbuild_order(self):
        unbuild_view = self.env.ref('pways_raw_multi_unbuild.sorting_order_tree_view')
        return {
            'name': _('Unbuild Orders'),
            'domain': [("project_id", "=", self.project_id.id)],
            'res_model': 'sorting.order',
            'type': 'ir.actions.act_window',
            'view_id': unbuild_view.id,
            'views': [(unbuild_view.id, 'tree'), (False, 'form')],
            'view_mode': 'tree,form',
        }


class ProjectEstimateLine(models.Model):
    _name = "project.estimate.line"
    _description = "Project Estimate Analysis Items"
    _rec_name = "product_id"

    description = fields.Text(string="Description")
    project_estimate_id = fields.Many2one("project.estimate", string="Project Estimate")
    parent_id = fields.Many2one("project.estimate.line", string="Parent Item")
    qty = fields.Float(string="Qty", default=1.0)
    price = fields.Float(string="Price")
    unbuild_template_id = fields.Many2one("sorting.template", string="Unbuild",
                                          domain="[('product_id', '=', product_id)]")
    product_id = fields.Many2one("product.product", string="Product")

    def _validate_unbuild_template(self):
        lines_ids = self.env["unbuild.estimate.line"].search([
            ("project_estimate_id", "=", self.project_estimate_id.id),
            ("unbuild_template_id", "=", self.unbuild_template_id.id),
        ])
        lines_ids.unlink()

    @api.depends('project_estimate_id.unbuild_line_ids')
    def _cal_subtotal(self):
        for rec in self:
            if rec.unbuild_template_id and rec.project_estimate_id.unbuild_line_ids:
                bom_estimate = self.env["unbuild.estimate.line"].search([
                    ("project_estimate_id", "=", rec.project_estimate_id.id),
                    ("unbuild_template_id", "=", rec.unbuild_template_id.id),
                ])
                rec.sub_total = sum([_.price * _.qty for _ in bom_estimate])
            else:
                rec.sub_total = rec.qty * rec.price

    sub_total = fields.Monetary(string="Total", compute=_cal_subtotal)
    currency_id = fields.Many2one("res.currency", string="Currency")
    qty = fields.Float(string="Qty", default=1.0)
    price = fields.Float(string="Price")

    def action_show_details(self):
        self.ensure_one()
        if self.unbuild_template_id:
            self._validate_unbuild_template()
            for bom in self._pull_bom(self.unbuild_template_id):
                self.project_estimate_id.update({
                    "unbuild_line_ids": [(0, 0, {
                        "product_id": bom.product_id.id,
                        "qty": bom.product_qty,
                        "product_uom_id": bom.product_uom_id.id,
                        "project_estimate_id": self.project_estimate_id.id,
                        "unbuild_template_id": self.unbuild_template_id.id,
                    })]
                })

    def _pull_bom(self, base_template_id):
        bom = []
        for line in base_template_id.sorting_line:
            bom.append(line)
            _bom_line = self.env["sorting.template"].search([("product_id", "=", line.product_id.id)], limit=1)
            if _bom_line.sorting_line:
                bom.append(_bom_line.sorting_line)
        return bom


class UnbuildItems(models.Model):
    _name = "unbuild.estimate.line"
    _description = "Unbuild Item Estimate"

    product_id = fields.Many2one("product.product", string="Product")
    project_estimate_id = fields.Many2one("project.estimate", string="Project Estimate")
    unbuild_template_id = fields.Many2one("sorting.template", string="Unbuild")
    qty = fields.Float(string="Qty", default=1.0)
    price = fields.Monetary(string="Price")
    currency_id = fields.Many2one("res.currency", string="Currency")

    @api.depends('qty', 'price')
    def _cal_subtotal(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.price

    sub_total = fields.Float(string="Total", compute=_cal_subtotal)
    product_uom_id = fields.Many2one("uom.uom", string="Product UOM", related="product_id.uom_id")
