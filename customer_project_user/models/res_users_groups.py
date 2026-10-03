# Copyright 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Group cleanup for Project Customer users.

The problem this solves
-----------------------
A Project Customer user should hold the customer group plus whatever is needed
to *use* the project UI — and nothing else.

On `ledningssystem` (measured 2026-10-03) the five Project Customer users held
32–55 groups each, including:

    payroll.group_payroll_manager          ← salaries
    hr.group_hr_manager                    ← all employee data
    hr.group_hr_user                       ← all employee data
    account.group_account_manager          ← full accounting
    sales_team.group_sale_manager          ← all sales data
    project.group_project_manager          ← all projects
    base.group_user                        ← the URL bypass

All five were written by one bulk operation on 2026-09-27 14:41:47 that touched
66 users. The module's `implied_ids` only ever granted `base.group_user`; the
rest came from that write.

This module cannot fix that from XML — group membership lives in
`res_groups_users_rel`, not in the module's data files. So the cleanup is an
explicit, repeatable operation.

Why repeatable
--------------
The same bulk operation that created the problem can recreate it. A manual UI
cleanup would be undone silently. This runs as a maintenance action and can be
re-run safely.

Scope
-----
Only users who are members of the customer group are touched. Other external
users with the same pattern (27 were found) are deliberately **out of scope** —
they are a separate finding and may include consultants for whom the groups are
intentional.
"""

import logging

from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

CUSTOMER_GROUP = "customer_project_user.group_project_customer_user"

# Groups a Project Customer is ALLOWED to keep. Everything else is removed.
#
# This is an allow-list, not a deny-list: a deny-list would silently permit
# every group added in the future, which is how the current situation arose.
#
# ⚠️ CRITICAL: no entry may imply base.group_user, directly or transitively.
# Group implication is transitive and Odoo has no "inherit the ACLs but not the
# implied groups" mechanism, so adding such a group re-opens the URL bypass.
# Verified against ledningssystem 2026-10-03 — see the note per entry.
#
# Justification per entry:
#   customer_project_user.group_project_customer_user
#       the point of the module. implies: nothing.
#   base.group_multi_currency
#       projects may show a foreign currency. implies: nothing.
#   uom.group_uom
#       timesheet hours use units of measure. implies: nothing.
#   project.group_project_stages
#   project.group_project_milestone
#   project.group_project_task_dependencies
#       feature flags; they default from group membership, and a customer
#       should see the same task form as a regular project user.
#       implies: nothing (verified).
#   base.group_partner_manager
#       EXCLUDED — it grants full CRUD on res.partner, so the customer could
#       browse all 3620 partners (verified 2026-10-03). The narrow need (show a
#       partner name on their own project/task, create a contact when adding a
#       collaborator) is served by the explicit read-only res.partner ACL in
#       security/groups.xml instead.
#
# EXCLUDED because they imply base.group_user (verified):
#   project.group_project_rating                 ← implies base.group_user
#   hr_timesheet.group_hr_timesheet_user         ← implies base.group_user
#   document_knowledge.group_document_user       ← implies base.group_user
#   document_knowledge.group_ir_attachment_user  ← implies base.group_user
#
#   These four would have re-opened the bypass. Their ACLs are supplied
#   instead by the mirror mechanism (models/ir_model_access.py), which copies
#   ir.model.access rows without taking the implication — the same technique
#   used for project.group_project_user.
#
# Deliberately NOT allowed, among others:
#   base.group_user                  ← the bypass
#   base.group_no_one                ← technical features
#   base.group_allow_export          ← exports everything they can read
#   base.group_sanitize_override     ← HTML sanitizer bypass
#   project.group_project_user       ← implies base.group_user
#   project.group_project_manager    ← all projects
#   hr.*                             ← employee data
#   payroll.*                        ← salaries
#   account.*                        ← accounting
#   sales_team.*                     ← sales data
#   maintenance.*, website.*, crm.*, mass_mailing.*, survey.*
ALLOWED_GROUPS = [
    "customer_project_user.group_project_customer_user",
    "base.group_multi_currency",
    "uom.group_uom",
    "project.group_project_stages",
    "project.group_project_milestone",
    "project.group_project_task_dependencies",
]


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _customer_allowed_group_ids(self):
        """Resolve ALLOWED_GROUPS to ids, warning on any that are missing.

        Also asserts that no allowed group implies base.group_user, directly or
        transitively. That assertion is the guard against re-opening the URL
        bypass by adding a group that looks innocent: four candidates
        (project.group_project_rating, hr_timesheet.group_hr_timesheet_user,
        document_knowledge.group_document_user,
        document_knowledge.group_ir_attachment_user) were excluded for exactly
        this reason on 2026-10-03.
        """
        ids = []
        for xmlid in ALLOWED_GROUPS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                ids.append(group.id)
            else:
                _logger.warning(
                    "customer_project_user: allowed group %s not found; "
                    "skipping",
                    xmlid,
                )

        base_user = self.env.ref("base.group_user", raise_if_not_found=False)
        if base_user:
            offenders = []
            for group in self.env["res.groups"].browse(ids):
                if base_user in group.trans_implied_ids:
                    offenders.append(group.display_name)
            if offenders:
                raise UserError(
                    self.env._(
                        "customer_project_user: ALLOWED_GROUPS contains "
                        "group(s) that imply base.group_user: %s. This would "
                        "re-open the URL bypass. Remove them from the "
                        "allow-list and mirror their ACLs instead.",
                        ", ".join(offenders),
                    )
                )
        return ids

    @api.model
    def _customer_cleanup_plan(self, dry_run=True):
        """Compute (and optionally apply) the group cleanup for customers.

        Returns a list of dicts describing what would change / changed:
            {user_id, login, removed: [(id, name)], kept: [(id, name)]}

        In dry-run mode nothing is written.
        """
        customer_group = self.env.ref(CUSTOMER_GROUP, raise_if_not_found=False)
        if not customer_group:
            _logger.warning(
                "customer_project_user: customer group not found; "
                "cleanup skipped"
            )
            return []

        allowed_ids = set(self._customer_allowed_group_ids())
        customers = self.sudo().search(
            [("groups_id", "in", customer_group.id)]
        )

        plan = []
        for user in customers:
            current = user.groups_id
            to_remove = current.filtered(lambda g: g.id not in allowed_ids)
            to_keep = current - to_remove

            entry = {
                "user_id": user.id,
                "login": user.login,
                "removed": [(g.id, g.display_name) for g in to_remove],
                "kept": [(g.id, g.display_name) for g in to_keep],
            }
            plan.append(entry)

            if not dry_run and to_remove:
                _logger.warning(
                    "customer_project_user: removing %s group(s) from %s: %s",
                    len(to_remove),
                    user.login,
                    ", ".join(to_remove.mapped("display_name")),
                )
                user.sudo().write({"groups_id": [(3, g.id) for g in to_remove]})

            # Ensure the allowed feature groups are actually present. Some
            # customers were never direct members of them (they reached the
            # features via base.group_user), so removing that group would
            # silently drop the features unless we add them back explicitly.
            if not dry_run:
                missing = [
                    gid for gid in allowed_ids if gid not in user.groups_id.ids
                ]
                if missing:
                    _logger.info(
                        "customer_project_user: adding %s allowed group(s) "
                        "to %s",
                        len(missing),
                        user.login,
                    )
                    user.sudo().write(
                        {"groups_id": [(4, gid) for gid in missing]}
                    )

        return plan

    @api.model
    def _customer_cleanup_apply(self):
        """Apply the cleanup. Returns the plan that was executed."""
        return self._customer_cleanup_plan(dry_run=False)
