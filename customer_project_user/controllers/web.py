from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.service import security
from odoo.addons.portal.controllers.web import Home as PortalHome
from odoo.addons.web.controllers.home import Home as WebHome
from odoo.addons.web.controllers.utils import ensure_db, is_user_internal

CUSTOMER_GROUP = 'customer_project_user.group_project_customer_user'
PROJECT_ACTION = 'project.open_view_project_all'


class ProjectCustomerHome(PortalHome):
    """Let a Project Customer reach the backend web client, and land in Project.

    Why this override exists
    ------------------------
    Two separate gates block a Project Customer from the backend, and both key
    off the same thing: ``is_user_internal()``, i.e.
    ``has_group('base.group_user')``. A Project Customer deliberately does NOT
    hold that group — holding it was the URL bypass this change removes
    (460 inherited ACL rows, ledningssystem 2026-10-03).

    Gate 1 — ``portal/controllers/web.py``::

        def index(self, *args, **kw):
            if request.session.uid and not is_user_internal(request.session.uid):
                return request.redirect_query('/my', query=request.params)
            return super().index(*args, **kw)

    Gate 2 — ``web/controllers/home.py``, inside ``web_client``::

        if not is_user_internal(request.session.uid):
            return request.redirect('/web/login_successful', 303)

    Verified against ledningssystem 2026-10-03 with the test customer
    lsbihi@sfa.fr:

        /odoo                                      -> /en/my
        /odoo/action-324                           -> /en/my?subpath=action-324
        /odoo/project.project/33/action_view_tasks -> /en/my?subpath=...

    So the customer was confined to the portal shell even though their ACL set
    already allowed project.project (1 row), project.task (110), sprint (58)
    and analytic line (105), and ``load_menus`` already returned a single
    "Projekt" root. The only thing missing was the route.

    Why ``web_client`` is reimplemented rather than delegated
    ---------------------------------------------------------
    Gate 2 lives *inside* the body of ``WebHome.web_client``, not in a hook.
    Calling ``WebHome.web_client(self, ...)`` would run the gate again, so the
    body is reproduced here with the customer branch added. The copied logic is
    Odoo 18's and is kept byte-for-byte where possible; the only change is that
    ``is_user_internal`` is replaced by ``_may_use_web_client``, which is true
    for internal users *and* Project Customers.

    This does not widen access. The customer still has no base.group_user, so
    the ACL set stays narrow and the menu tree stays limited to Project. The
    override changes *which route is reachable*, not *what the route may read*.

    Landing
    -------
    ``_login_redirect`` is also overridden: the portal Home returns '/my' for
    any non-internal user, and the web Home returns '/web/login_successful'.
    Neither is where a Project Customer belongs. They land on the Project
    action, which is the only menu root they have.

    ``res.users.action_id`` is set to the same action (models/res_users.py) as
    a second, declarative guard: it is the documented Odoo mechanism for
    "action to open at log on".
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_project_customer(self, uid=None):
        """True when the given (or logged-in) user is a Project Customer."""
        uid = uid or request.session.uid
        if not uid:
            return False
        return request.env['res.users'].sudo().browse(uid).has_group(
            CUSTOMER_GROUP
        )

    def _may_use_web_client(self, uid):
        """Internal users keep the stock behaviour; customers are added.

        This is the single predicate both gates are routed through.
        """
        return is_user_internal(uid) or self._is_project_customer(uid)

    # ------------------------------------------------------------------
    # Gate 1: the portal Home redirect
    # ------------------------------------------------------------------

    @http.route()
    def index(self, s_action=None, db=None, **kw):
        if request.db and request.session.uid and not self._may_use_web_client(
            request.session.uid
        ):
            return request.redirect_query(
                '/web/login_successful', query=request.params
            )
        return request.redirect_query('/odoo', query=request.params)

    # ------------------------------------------------------------------
    # Gate 2: the web client itself
    # ------------------------------------------------------------------

    @http.route()
    def web_client(self, s_action=None, **kw):
        # Ensure we have both a database and a user
        ensure_db()
        if not request.session.uid:
            return request.redirect_query(
                '/web/login', query={'redirect': request.httprequest.full_path},
                code=303,
            )
        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)
        if not security.check_session(request.session, request.env, request):
            raise http.SessionExpiredException("Session expired")
        # --- the one changed line: internal users OR Project Customers ---
        if not self._may_use_web_client(request.session.uid):
            return request.redirect('/web/login_successful', 303)

        # Side-effect, refresh the session lifetime
        request.session.touch()

        # Restore the user on the environment, it was lost due to auth="none"
        request.update_env(user=request.session.uid)
        try:
            if request.env.user:
                request.env.user._on_webclient_bootstrap()
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return request.redirect('/web/login?error=access')

    # ------------------------------------------------------------------
    # Landing
    # ------------------------------------------------------------------

    def _login_redirect(self, uid, redirect=None):
        result = super()._login_redirect(uid, redirect=redirect)
        if not self._is_project_customer(uid):
            return result

        # The portal Home returns '/my' for every non-internal user, and the
        # web Home returns '/web/login_successful'. A Project Customer is
        # non-internal by design, so without this they would land on one of
        # those instead of their project. An explicit redirect is honoured.
        if redirect:
            return result

        action = request.env.ref(PROJECT_ACTION, raise_if_not_found=False)
        if action:
            return '/odoo/action-%d' % action.id
        return result
