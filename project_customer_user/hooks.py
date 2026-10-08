# Copyright 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Install/upgrade hooks for the Project Customer ACL mirror.

The mirror must run:
  - on install (post_init_hook), and
  - on every upgrade, so a newly installed Project-adjacent module that ships
    its ACLs on its own group is picked up.

Odoo has no post_upgrade_hook, so the upgrade path is a migration script in
``migrations/<version>/post-*.py`` that calls the same sync method. See
``migrations/18.0.0.2.0/post-mirror_acl.py``.

Module name
-----------
This module was renamed from ``customer_project_user`` to
``project_customer_user`` in 18.0.1.0.0, to match the ``project_*`` naming of
the rest of the odoo-project repository. The rename is carried by
``migrations/18.0.1.0.0/post-rename_module.py``, which re-points the module's
ir.model.data rows so the existing group and its memberships survive. The
hooks below are name-agnostic — they resolve the group through
``env.ref`` on the new xmlid.
"""

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Run the ACL mirror and the deny layer right after install."""
    _logger.info("project_customer_user: running ACL mirror (post_init_hook)")
    env["ir.model.access"]._mirror_sync_customer_acl()
    _logger.info("project_customer_user: running deny layer (post_init_hook)")
    env["ir.rule"]._deny_sync_customer_rules()
    env["res.users"]._customer_apply_landing_action()


def post_load_hook(env):
    """Re-sync the derived security data after every registry load.

    Why this exists (found 2026-10-03)
    ----------------------------------
    The deny layer and the ACL mirror are *derived* from the whitelist in
    models/ir_rule.py and models/res_users_groups.py. Odoo only runs
    migrations when the manifest version changes, so editing the whitelist
    without bumping the version left stale rules behind:

        sprint.module was added to ALLOWED_MODELS, but its deny rule survived
        because 18.0.0.3.0 had already been migrated. The customer saw 0 of
        2098 modules and the "Modules" dropdown on a task was empty.

    Running the sync on every registry load removes that trap: the whitelist in
    the code is always the truth, with no version bump required. Both syncs are
    idempotent and cheap (a handful of searches), and they run as the registry
    loads rather than per request.
    """
    try:
        env["ir.model.access"]._mirror_sync_customer_acl()
        env["ir.rule"]._deny_sync_customer_rules()
    except Exception:  # never break a registry load
        _logger.exception(
            "project_customer_user: security sync failed on registry load"
        )


def uninstall_hook(env):
    """Clear mirrored ACL rows and deny rules when the module is uninstalled.

    Without this, uninstalling the module would leave the rows behind (they
    belong to a group that is about to disappear, but the rows are ordinary
    ir.model.access / ir.rule records and are not removed automatically).
    """
    _logger.info("project_customer_user: clearing ACL mirror (uninstall_hook)")
    env["ir.model.access"]._mirror_clear_customer_acl()
    _logger.info("project_customer_user: clearing deny layer (uninstall_hook)")
    env["ir.rule"]._deny_clear_customer_rules()
