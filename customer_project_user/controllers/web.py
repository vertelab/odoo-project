from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home


class ProjectCustomerHome(Home):

    def _login_redirect(self, uid, redirect=None):
        result = super()._login_redirect(uid, redirect=redirect)
        if result in ('/odoo', '/web', False, None):
            user = request.env['res.users'].sudo().browse(uid)
            # Use the same predicate as the record rules (design D5). This used
            # to duplicate a narrower domain, so a customer reachable only via
            # message_partner_ids got access but was not counted here, and the
            # redirect fell through to the full project list.
            if user.has_group('customer_project_user.group_project_customer_user'):
                domain = request.env['project.project']._customer_project_domain(
                    partner=user.partner_id
                )
                projects = request.env['project.project'].sudo().search(domain)
                if len(projects) == 1:
                    return '/odoo/project.project/%d/action_view_tasks' % projects.id
                return '/odoo/project.open_view_project_all'
        return result
