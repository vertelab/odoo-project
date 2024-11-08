from odoo import models, fields, api


class Users(models.Model):
    _inherit = "res.users"

    def _is_customer_user(self):
        self.ensure_one()
        return self.has_group('customer_project_user.group_project_customer_user')
