from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def get_user_roots(self):
        if self.env.user.has_group('customer_project_user.group_project_customer_user'):
            project_root = self.env.ref('project.menu_main_pm', raise_if_not_found=False)
            if project_root:
                return self.search([('id', '=', project_root.id)])
        return super().get_user_roots()
