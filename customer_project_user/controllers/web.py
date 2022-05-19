# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.portal.controllers.web import Home
#from odoo.addons.web.controllers.main import Home
from odoo.http import request


class HomeExtended(Home):

    @http.route()
    def index(self, *args, **kw):
        if request.session.uid and not (request.env['res.users'].sudo().browse(request.session.uid).has_group('base.group_user') or request.env['res.users'].sudo().browse(request.session.uid).has_group('customer_project_user.group_project_customer_user')):
            return http.local_redirect('/my', query=request.params, keep_hash=True)
        return super(Home, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not (request.env['res.users'].sudo().browse(request.session.uid).has_group('base.group_user') or request.env['res.users'].sudo().browse(request.session.uid).has_group('customer_project_user.group_project_customer_user')):
            redirect = '/my'
        return super(Home, self)._login_redirect(uid, redirect=redirect)


    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        if request.session.uid and not (request.env['res.users'].sudo().browse(request.session.uid).has_group('base.group_user') or request.env['res.users'].sudo().browse(request.session.uid).has_group('customer_project_user.group_project_customer_user')):
            return http.local_redirect('/my', query=request.params, keep_hash=True)
        return super(Home, self).web_client(s_action, **kw)