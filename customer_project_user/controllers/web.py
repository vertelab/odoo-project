from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home


class ProjectCustomerHome(Home):

    def _login_redirect(self, uid, redirect=None):
        result = super()._login_redirect(uid, redirect=redirect)
        if result in ('/odoo', '/web', False, None):
            user = request.env['res.users'].sudo().browse(uid)
            if user.has_group('customer_project_user.group_project_customer_user'):
                projects = request.env['project.project'].sudo().search([
                    '|', ('partner_id', '=', user.partner_id.id),
                    ('customer_ids', 'in', [user.partner_id.id]),
                ])
                if len(projects) == 1:
                    return '/odoo/project.project/%d/action_view_tasks' % projects.id
                return '/odoo/project.open_view_project_all'
        return result
