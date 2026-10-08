# Copyright 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Upgrade path for the Project Customer ACL mirror.

Odoo has no post_upgrade_hook, so the mirror is re-synced from a migration
script. This runs on every ``-u project_customer_user`` once the version in the
manifest reaches 18.0.0.2.0 or later.

NOTE — the historical module name
---------------------------------
This migration predates the 18.0.1.0.0 rename (customer_project_user ->
project_customer_user). The SQL below deliberately keeps
``d.module = 'customer_project_user'``: it runs against a database whose
ir.model.data rows still carry the old module name at the point this migration
is applied, because ``migrations/18.0.1.0.0/post-rename_module.py`` runs only
after the version reaches 18.0.1.0.0. Do not "fix" the module name here —
changing it would make the migration miss the group on a database upgraded
from an older version.

Two jobs
--------
1. **Remove the stale ``base.group_user`` implication.** Removing
   ``implied_ids`` from the XML is not enough: Odoo does not delete m2m rows
   that disappear from the XML, so the implication survives the upgrade and the
   bypass stays open. This was observed live on 2026-10-03 — after the first
   ``-u`` the group still implied "Internal User" (res_groups_implied_rel
   gid=88, hid=1). The row must be deleted explicitly.

2. **Re-sync the ACL mirror.** The mirror's whole point is that installing a
   new Project-adjacent module requires no human ACL work. That only holds if
   the sync runs again after the new module's ACLs exist — i.e. on upgrade.
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        # Fresh install: post_init_hook handles the mirror. The implication is
        # absent by construction on a fresh install.
        return

    _logger.info(
        "project_customer_user: running migration from version %s", version
    )

    # ------------------------------------------------------------------
    # 1. Delete the stale base.group_user implication (design D2)
    # ------------------------------------------------------------------
    cr.execute(
        """
        SELECT r.gid, r.hid
          FROM res_groups_implied_rel r
          JOIN ir_model_data d
            ON d.res_id = r.gid AND d.model = 'res.groups'
         WHERE d.module = 'customer_project_user'
           AND d.name = 'group_project_customer_user'
        """
    )
    customer_gid = None
    for gid, hid in cr.fetchall():
        customer_gid = gid
        # Resolve the implied group's xmlid to decide whether to drop it.
        cr.execute(
            """
            SELECT module || '.' || name
              FROM ir_model_data
             WHERE model = 'res.groups' AND res_id = %s
            """,
            (hid,),
        )
        row = cr.fetchone()
        implied_xmlid = row[0] if row else None
        if implied_xmlid in (
            "base.group_user",
            "project.group_project_user",
            "hr_timesheet.group_hr_timesheet_user",
        ):
            _logger.warning(
                "project_customer_user: removing stale implication "
                "%s (gid=%s hid=%s) — it reopens the URL bypass",
                implied_xmlid,
                gid,
                hid,
            )
            cr.execute(
                "DELETE FROM res_groups_implied_rel WHERE gid = %s AND hid = %s",
                (gid, hid),
            )

    # ------------------------------------------------------------------
    # 2. Re-sync the ACL mirror
    # ------------------------------------------------------------------
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.model.access"]._mirror_sync_customer_acl()
