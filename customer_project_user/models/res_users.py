from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _is_internal(self):
        self.ensure_one()
        return super()._is_internal() or self.sudo().has_group('customer_project_user.group_project_customer_user')
