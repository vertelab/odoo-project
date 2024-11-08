# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError
from odoo.addons.portal.controllers.web import Home as PortalHome
from odoo.addons.web.controllers.home import Home as WebHome
from odoo.addons.web.controllers.utils import is_user_internal, ensure_db
from odoo.addons.customer_project_user.controllers.utils import is_customer_user
from odoo.http import request
from odoo.service import security


class HomeExtended(WebHome):

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        if request.db and request.session.uid and not (
                is_user_internal(request.session.uid) or is_customer_user(request.session.uid)
        ):
            return request.redirect_query('/web/login_successful', query=request.params)
        return request.redirect_query('/web', query=request.params)

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):

        # Ensure we have both a database and a user
        ensure_db()
        if not request.session.uid:
            return request.redirect_query('/web/login', query=request.params, code=303)
        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)
        if not security.check_session(request.session, request.env):
            raise http.SessionExpiredException("Session expired")
        if not (is_user_internal(request.session.uid) or is_customer_user(request.session.uid)):
            return request.redirect('/web/login_successful', 303)

        # Side-effect, refresh the session lifetime
        request.session.touch()

        # Restore the user on the environment, it was lost due to auth="none"
        request.update_env(user=request.session.uid)
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return request.redirect('/web/login?error=access')


class PortalExtended(PortalHome):

    @http.route('/', type='http', auth="none")
    def index(self, *args, **kw):
        if request.session.uid and not (
                is_user_internal(request.session.uid) or is_customer_user(request.session.uid)
        ):
            return request.redirect_query('/my', query=request.params)
        return super(PortalHome, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not (is_user_internal(uid) or is_customer_user(uid)):
            redirect = '/my'
        return super(PortalHome, self)._login_redirect(uid, redirect=redirect)

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):

        if request.session.uid and not (
                is_user_internal(request.session.uid) or is_customer_user(request.session.uid)
        ):
            return request.redirect_query('/my', query=request.params)
        return super(PortalHome, self).web_client(s_action, **kw)
