# Copyright 2026 Vertel Sverige AB (<https://vertel.se/>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Upgrade path for the ALLOWED_GROUPS allow-list.

Odoo has no post_upgrade_hook, so the group sync is re-run from a migration
script — the same pattern the ACL mirror and the deny layer already use.

What changed in 18.0.0.3.2
--------------------------
``base.group_allow_export`` ("Access to export feature") was added to
``ALLOWED_GROUPS``. The operator's report was "det finns inte alternativet att
exportera" — a Project Customer had no Export entry in the list cog menu.

The group was already correct in the code, but ``ALLOWED_GROUPS`` had no
automatic application path: it was only ever applied by the manual cleanup
action, so an existing customer never received it. This migration applies it,
and ``hooks.post_load_hook`` keeps applying it from now on.

Additive only — nothing is removed here. Removing groups is the cleanup
action's job, and that stays a human decision.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        # Fresh install: post_init_hook handles the sync.
        return

    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    granted = env["res.users"]._customer_sync_allowed_groups()
    _logger.info(
        "project_customer_user: granted allowed groups to %s customer(s)",
        granted,
    )

    # Re-sync the deny layer afterwards: the set of models to deny is derived
    # from the ACLs the customer users hold, and base.group_allow_export adds
    # one (ir.exports). It is whitelisted, but the rule set must be recomputed
    # so a future group added to the allow-list cannot silently widen access.
    env["ir.rule"]._deny_sync_customer_rules()
