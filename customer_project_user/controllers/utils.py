from odoo.http import request


def is_customer_user(uid):
    return request.env['res.users'].browse(uid)._is_customer_user()
