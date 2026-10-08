# Copyright 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""ACL mirror for Project Customer users.

Why this exists
---------------
The customer group must give a customer the same rights as a regular project
user *inside a project they are shared on*, and nothing outside it (design D1).

Odoo grants Project ACLs to ``project.group_project_user``, which implies
``base.group_user``. We cannot imply that group (it would re-import the full
internal surface — 460 ACL rows, ledningssystem 2026-10-03) and Odoo offers no
"inherit the ACLs but not the implied groups" mechanism.

So we copy the ACL rows instead: for every ``ir.model.access`` row attached to
a declared *source group*, ensure an equivalent row exists for the customer
group — without ever taking the implication.

The ceiling (design D1/D4)
--------------------------
The customer gets the source group's permissions, minus ``perm_unlink`` on
``project.project`` and ``project.task``. Deleting project records is not part
of "using the project" and is the one action a reviewer cannot undo. Everything
else mirrors the source group.

Maintenance
-----------
The mirror runs on install and on every upgrade, so a newly installed
Project-adjacent module that ships its ACLs on its own group is picked up on
the next ``-u`` with no human in the loop. Rows whose source row disappeared are
deleted, so the customer's ACL set cannot grow monotonically.

Adding a source group
---------------------
Append it to ``SOURCE_GROUPS`` below. That is the whole checklist.
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

CUSTOMER_GROUP = "project_customer_user.group_project_customer_user"

# Groups whose ACLs are mirrored onto the customer group. Never implied.
SOURCE_GROUPS = [
    "project.group_project_user",
    "hr_timesheet.group_hr_timesheet_user",
]

# Models where the customer never receives perm_unlink, regardless of source.
# (project.project, project.task) — see design D1/D4.
UNLINK_DENY = [
    "project.project",
    "project.task",
]

# Marker so mirrored rows are recognisable and removable without touching
# rows a human created by hand.
MIRROR_PREFIX = "[mirror] "


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @api.model
    def _mirror_customer_group(self):
        """Return the customer group, or an empty recordset if not present."""
        return self.env.ref(CUSTOMER_GROUP, raise_if_not_found=False)

    @api.model
    def _mirror_source_groups(self):
        """Return the declared source groups that exist in this database."""
        groups = self.env["res.groups"]
        for xmlid in SOURCE_GROUPS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                groups |= group
            else:
                _logger.warning(
                    "project_customer_user: source group %s not found; "
                    "its ACLs will not be mirrored",
                    xmlid,
                )
        return groups

    @api.model
    def _mirror_desired_rows(self, customer_group, source_groups):
        """Compute the ACL rows the customer group should have.

        Returns a dict keyed by (model_id, name) -> values dict.
        """
        desired = {}
        for source in source_groups:
            rows = self.sudo().search(
                [("group_id", "=", source.id), ("active", "=", True)]
            )
            for row in rows:
                model_name = row.model_id.model
                perms = {
                    "perm_read": row.perm_read,
                    "perm_write": row.perm_write,
                    "perm_create": row.perm_create,
                    "perm_unlink": row.perm_unlink,
                }
                # Ceiling: never unlink on the protected models.
                if model_name in UNLINK_DENY:
                    perms["perm_unlink"] = False

                key = (row.model_id.id, row.name)
                if key in desired:
                    # Two source groups grant the same model: take the union,
                    # but keep the ceiling. This is what makes the combination
                    # of project (read-only on project.project) and
                    # hr_timesheet (inert there) produce a sane result, and
                    # what stops a later source from silently widening unlink.
                    existing = desired[key]
                    for field, value in perms.items():
                        if field == "perm_unlink" and model_name in UNLINK_DENY:
                            existing[field] = False
                        else:
                            existing[field] = existing[field] or value
                else:
                    desired[key] = dict(
                        perms,
                        name=MIRROR_PREFIX + row.name,
                        model_id=row.model_id.id,
                        group_id=customer_group.id,
                        active=True,
                    )
        return desired

    @api.model
    def _mirror_sync_customer_acl(self):
        """Make the customer group's mirrored ACL rows match the source groups.

        Idempotent: safe to run on every install/upgrade.
        """
        customer_group = self._mirror_customer_group()
        if not customer_group:
            _logger.warning(
                "project_customer_user: customer group not found; "
                "ACL mirror skipped"
            )
            return

        source_groups = self._mirror_source_groups()
        desired = self._mirror_desired_rows(customer_group, source_groups)

        existing = self.sudo().search(
            [
                ("group_id", "=", customer_group.id),
                ("name", "like", MIRROR_PREFIX + "%"),
            ]
        )
        existing_by_key = {(row.model_id.id, row.name): row for row in existing}

        created = updated = removed = 0

        # Create or update.
        for key, values in desired.items():
            row = existing_by_key.pop(key, None)
            if row is None:
                self.sudo().create(values)
                created += 1
            else:
                changed = {
                    field: values[field]
                    for field in (
                        "perm_read",
                        "perm_write",
                        "perm_create",
                        "perm_unlink",
                    )
                    if row[field] != values[field]
                }
                if changed:
                    row.sudo().write(changed)
                    updated += 1

        # Delete mirrored rows whose source row no longer exists. This is what
        # prevents monotonic growth and permanently-stuck permissions.
        if existing_by_key:
            stale = self.sudo().browse(
                [row.id for row in existing_by_key.values()]
            )
            removed = len(stale)
            stale.sudo().unlink()

        _logger.info(
            "project_customer_user: ACL mirror synced "
            "(created=%s updated=%s removed=%s, sources=%s)",
            created,
            updated,
            removed,
            ", ".join(source_groups.mapped("display_name")) or "none",
        )

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    @api.model
    def _mirror_clear_customer_acl(self):
        """Remove every mirrored row for the customer group.

        Used by the rollback path (design Migration Plan): a rolled-back
        instance must not silently keep the wider ACL set.
        """
        customer_group = self._mirror_customer_group()
        if not customer_group:
            return 0
        rows = self.sudo().search(
            [
                ("group_id", "=", customer_group.id),
                ("name", "like", MIRROR_PREFIX + "%"),
            ]
        )
        count = len(rows)
        rows.sudo().unlink()
        _logger.info(
            "project_customer_user: ACL mirror cleared (%s rows)", count
        )
        return count
