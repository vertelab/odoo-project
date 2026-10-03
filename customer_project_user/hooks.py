# Copyright 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Install/upgrade hooks for the Project Customer ACL mirror.

The mirror must run:
  - on install (post_init_hook), and
  - on every upgrade, so a newly installed Project-adjacent module that ships
    its ACLs on its own group is picked up.

Odoo has no post_upgrade_hook, so the upgrade path is a migration script in
``migrations/<version>/post-*.py`` that calls the same sync method. See
``migrations/18.0.0.2.0/post-mirror_acl.py``.
"""

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Run the ACL mirror and the deny layer right after install."""
    _logger.info("customer_project_user: running ACL mirror (post_init_hook)")
    env["ir.model.access"]._mirror_sync_customer_acl()
    _logger.info("customer_project_user: running deny layer (post_init_hook)")
    env["ir.rule"]._deny_sync_customer_rules()
    env["res.users"]._customer_apply_landing_action()


def uninstall_hook(env):
    """Clear mirrored ACL rows and deny rules when the module is uninstalled.

    Without this, uninstalling the module would leave the rows behind (they
    belong to a group that is about to disappear, but the rows are ordinary
    ir.model.access / ir.rule records and are not removed automatically).
    """
    _logger.info("customer_project_user: clearing ACL mirror (uninstall_hook)")
    env["ir.model.access"]._mirror_clear_customer_acl()
    _logger.info("customer_project_user: clearing deny layer (uninstall_hook)")
    env["ir.rule"]._deny_clear_customer_rules()
