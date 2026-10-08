# Copyright 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Upgrade path for the Project Customer ACL mirror and deny layer.

Odoo has no post_upgrade_hook, so both are re-synced from a migration script.
This runs on every ``-u project_customer_user`` once the manifest version
reaches 18.0.0.3.0 or later.

NOTE — the historical module name
---------------------------------
This migration predates the 18.0.1.0.0 rename (customer_project_user ->
project_customer_user). Odoo runs migrations in version order, so on a database
upgraded from an older version this script runs *before*
``migrations/18.0.1.0.0/post-rename_module.py`` — i.e. while the group's xmlid
still carries the old module prefix. ``_customer_group()`` below therefore
resolves the group under either name; do not replace it with a single
``env.ref``.

History — why the direction reversed
------------------------------------
18.0.0.2.0 removed the ``base.group_user`` implication and the
``_is_internal()`` override, on the theory that the customer could be a
non-internal backend user. That theory does not hold in Odoo 18:

  - ``portal/controllers/web.py`` redirects every non-internal user from
    /odoo to /my, and
  - ``web/models/ir_http.py`` only emits ``user_companies`` in session_info
    when ``is_internal_user`` is true, so the JS client dies on
    ``Cannot read properties of undefined (reading 'allowed_companies')``.

The operator's decision (2026-10-03) is that the backend is the requirement.
So 18.0.0.3.0 restores ``base.group_user`` and solves the over-permission with
an explicit deny layer instead (one ``ir.rule`` per non-whitelisted model,
``domain_force = [(0,'=',1)]``).

Three jobs
----------
1. **Restore the ``base.group_user`` implication.** Odoo does not always
   re-create m2m rows reliably when only the XML changes on an already
   installed module, and the row was explicitly deleted by the 18.0.0.2.0
   migration. Writing it here is idempotent and removes the doubt.

2. **Re-sync the ACL mirror.** The mirror's whole point is that installing a
   new Project-adjacent module requires no human ACL work. That only holds if
   the sync runs again after the new module's ACLs exist — i.e. on upgrade.

3. **Sync the deny layer.** Same reasoning, plus it must run *after* the
   implication is restored, because the set of models to deny is derived from
   the ACLs the customer group holds.
"""

import logging

_logger = logging.getLogger(__name__)


def _customer_group(env):
    """Resolve the customer group under either module name.

    See the note in the module docstring: on a database upgraded from before
    the rename, this migration runs while the xmlid is still
    ``customer_project_user.group_project_customer_user``.
    """
    for xmlid in (
        "project_customer_user.group_project_customer_user",
        "customer_project_user.group_project_customer_user",
    ):
        group = env.ref(xmlid, raise_if_not_found=False)
        if group:
            return group
    return env["res.groups"]


def migrate(cr, version):
    if not version:
        return

    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # 1. Restore the base.group_user implication.
    customer_group = _customer_group(env)
    internal = env.ref("base.group_user", raise_if_not_found=False)
    if customer_group and internal:
        if internal not in customer_group.implied_ids:
            customer_group.write({"implied_ids": [(4, internal.id)]})
            _logger.info(
                "project_customer_user: restored base.group_user implication"
            )

    # 2. Re-sync the ACL mirror.
    env["ir.model.access"]._mirror_sync_customer_acl()

    # 3. Sync the deny layer (after the implication, so the reachable-model
    #    set is complete).
    env["ir.rule"]._deny_sync_customer_rules()

    # 4. Make sure every customer lands on the project action.
    env["res.users"]._customer_apply_landing_action()
