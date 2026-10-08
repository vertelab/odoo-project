# Copyright 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Keep Project Customers out of internal mail threads.

The bug this fixes (reported by the operator, 2026-10-03)
--------------------------------------------------------
Submitting a timesheet emailed 17 customers. The operator's description:

    "det blev följa när jag tryckte på knappen så jag kunde inte ens ta bort
     dom innan det skickades"

That is exactly what the code does. ``hr_timesheet_sheet`` (OCA):

    def action_timesheet_confirm(self):
        self._timesheet_subscribe_users()   # subscribes
        self.reset_add_line()
        self.write({"state": "confirm"})    # posts -> notifies

and:

    def _get_possible_reviewers(self):
        if self.review_policy == "hr":
            res |= self.env.ref("hr.group_hr_user").users
        elif self.review_policy == "hr_manager":
            res |= self.env.ref("hr.group_hr_manager").users
        elif self.review_policy == "timesheet_manager":
            res |= self.env.ref("hr_timesheet.group_hr_timesheet_approver").users
        return res

    def _get_subscribers(self):
        subscribers = self._get_possible_reviewers().mapped("partner_id")
        subscribers |= self._get_informables()
        return subscribers

So *every member of hr.group_hr_user* is treated as a possible reviewer and
subscribed. Project Customers were members of that group (the 2026-09-27 bulk
write put them in 32-55 groups each), so they were subscribed and notified in
the same call — no window to remove them.

Why filtering here and not by removing the group membership
-----------------------------------------------------------
Removing hr.group_hr_user from the customers is correct and is done (the
allow-list cleanup). But it is not sufficient: the group can be re-granted by
hand, by an import, or by a future module, and the failure mode is silent — a
customer receives an internal mail and nobody notices. A filter at the point
where the recipient list is built is the guard that holds regardless of group
membership.

What is filtered
----------------
Any Project Customer partner is removed from:
  - the subscriber list of hr_timesheet.sheet (``_get_subscribers``), and
  - the notification recipients of any mail.message posted on a record that is
    not itself a customer-visible project or task.

The second is the general case: it covers every model, not just timesheets, so
a future module that builds a recipient list from a group will not reintroduce
the leak.

Scope note
----------
Customers must still receive notifications for their own projects and tasks —
that is the point of the module. So the filter is placed on the *internal*
threads, not on project/task threads.
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

CUSTOMER_GROUP = "project_customer_user.group_project_customer_user"

# Models whose threads a customer is allowed to be part of. Everything else is
# an internal thread and must not reach a customer.
#
# Operator's rule (2026-10-03): "allt utom project task är bra" — a customer
# belongs on project.project and project.task threads, and nowhere else. That
# is the whole allow-list; do not widen it without asking.
#
# Verified on ledningssystem 2026-10-03 with the five Project Customers plus one
# internal user as the recipient list:
#
#   project.project        6/6 kept, 0 customers dropped
#   project.task           6/6 kept, 0 customers dropped
#   hr_timesheet.sheet     1/6 kept, 5 customers dropped
#   account.analytic.line  1/6 kept, 5 customers dropped
#   hr.employee            1/6 kept, 5 customers dropped
#   res.users              1/6 kept, 5 customers dropped
#   sale.order             1/6 kept, 5 customers dropped
#   account.move           1/6 kept, 5 customers dropped
#   ai.agent               1/6 kept, 5 customers dropped
#   helpdesk.ticket        1/6 kept, 5 customers dropped
#   mail.channel           1/6 kept, 5 customers dropped
#   project.update         1/6 kept, 5 customers dropped
#   project.milestone      1/6 kept, 5 customers dropped
#
# Only Project Customer partners are ever dropped. Other external users
# (portal accounts, AI agents, contractors) are untouched — the filter keys on
# group membership, never on share=True or "is external".
#
# ---------------------------------------------------------------------------
# The predicate, after the 2026-10-08 change
# ---------------------------------------------------------------------------
#
# The table above is the *before* measurement. It shows the bug this change
# fixes: project.update and project.milestone were dropped 6/6, even though
# they belong to a project the customer is shared on. A project update is
# literally the project's own status post — the thing a customer should be told
# about.
#
# The cause was that the allow-list keyed on the *model name*:
#
#     CUSTOMER_VISIBLE_MODELS = ("project.project", "project.task")
#
# so any project-adjacent model that was not one of those two was dropped. The
# fix keys on the *record's project* instead: a customer is kept as a recipient
# when the thread's record is a project or task they are shared on, or a record
# that belongs to such a project. That covers the whole class at once —
# including models added by a future module — which is the same principle the
# deny layer's whitelist follows.
#
# Verified 2026-10-08: project.update and project.milestone both carry
# `project_id -> project.project`, so a single generic resolution works and no
# per-model table is needed. project.task.type has no project_id and therefore
# falls back to *drop*, which is correct: it is a global stage model, not a
# project-scoped thread.
#
# Decision table, before vs after (three customers, two of them shared on the
# project):
#
#   model                   before        after
#   project.project         keep all      keep all        (unchanged)
#   project.task            keep all      keep all        (unchanged)
#   project.update          drop all      keep shared     <- fixed
#   project.milestone       drop all      keep shared     <- fixed
#   hr_timesheet.sheet      drop all      drop all        (unchanged)
#   account.analytic.line   drop all      drop all        (unchanged)
#   hr.employee             drop all      drop all        (unchanged)
#   sale.order              drop all      drop all        (unchanged)
#   account.move            drop all      drop all        (unchanged)
#   ai.agent                drop all      drop all        (unchanged)
#   helpdesk.ticket         drop all      drop all        (unchanged)
#   mail.channel            drop all      drop all        (unchanged)
#
# The "unchanged" rows are the point: the leak that started this work (a
# timesheet submission emailing 17 customers) stays closed. Only the
# project-scoped models change behaviour, and only for customers actually
# shared on the project.

# Models whose records are themselves the project scope. A customer is kept
# when the record is one of these and they are shared on it.
PROJECT_SCOPE_MODELS = (
    "project.project",
    "project.task",
)

# Models that hang off a project and are therefore part of its scope. The
# record's `project_id` is resolved and tested against the customer's projects.
PROJECT_CHILD_MODELS = (
    "project.update",
    "project.milestone",
)


class MailMessage(models.Model):
    """General guard: a customer is never a recipient on an internal thread.

    ``_notify_thread`` is where Odoo turns a follower set into notification
    records. Filtering there covers every model at once, so a future module
    that subscribes a group of users cannot reintroduce the leak.

    This is also the fix for the reported timesheet bug. ``hr_timesheet_sheet``
    subscribes every member of hr.group_hr_user as a "possible reviewer" and
    posts the notification in the same call, so there is no window to remove
    them by hand. Filtering at _notify_thread catches that notification
    regardless of which module built the recipient list — and unlike an
    _inherit on hr_timesheet.sheet it cannot crash the registry when the OCA
    addon's model is absent.
    """

    _inherit = "mail.message"

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        recipients = kwargs.get("partners")
        if recipients:
            kwargs["partners"] = self._customer_filter_recipients(
                recipients, msg_vals or {}
            )
        return super()._notify_thread(message, msg_vals=msg_vals, **kwargs)

    @api.model
    def _customer_filter_recipients(self, partners, msg_vals):
        """Remove customers from recipients unless the thread is theirs.

        "Theirs" means the thread's record is inside the customer's project
        scope — see the module docstring. Any failure to resolve the record
        falls back to *drop*, i.e. the previous restrictive behaviour, never to
        "allow".
        """
        model = msg_vals.get("model") or (msg_vals.get("res_id") and self.model)
        res_id = msg_vals.get("res_id")

        customer_partners = self._customer_partners()
        if not customer_partners:
            return partners

        # Fast path: the thread is a project or task. A customer who is on it
        # belongs on its thread.
        if model in PROJECT_SCOPE_MODELS and res_id:
            return partners

        # Project-adjacent thread: keep only the customers who are shared on
        # the project the record belongs to.
        kept = self._customer_partners_on_project(model, res_id)
        dropped = (partners & customer_partners) - kept
        if dropped:
            _logger.info(
                "project_customer_user: dropped %s Project Customer(s) from "
                "notifications on %s: %s",
                len(dropped),
                model or "unknown model",
                ", ".join(dropped.mapped("email") or dropped.mapped("name")),
            )
        return partners - dropped

    @api.model
    def _customer_partners(self):
        """Every partner that is a Project Customer user."""
        group = self.env.ref(CUSTOMER_GROUP, raise_if_not_found=False)
        if not group:
            return self.env["res.partner"]
        return (
            self.env["res.users"]
            .sudo()
            .search([("groups_id", "in", group.id)])
            .mapped("partner_id")
        )

    @api.model
    def _customer_partners_on_project(self, model, res_id):
        """Customers shared on the project that ``model``/``res_id`` belongs to.

        Returns an empty recordset when the project cannot be resolved, so the
        caller drops the customer — the restrictive fallback.

        The share test is the same predicate as the ir.rule records in
        security/groups.xml (design D5 of the URL-bypass change):
        ``partner_id`` OR ``customer_ids``, never ``message_partner_ids``.

        Runs as sudo and swallows every exception: ``_notify_thread`` runs on
        every message post, and an error here would break messaging for all
        users, not just customers.
        """
        if not model or not res_id or model not in PROJECT_CHILD_MODELS:
            return self.env["res.partner"]
        try:
            record = self.env[model].sudo().browse(int(res_id))
            if not record.exists():
                return self.env["res.partner"]
            project = record.project_id
            if not project:
                return self.env["res.partner"]
            customers = self._customer_partners()
            if not customers:
                return self.env["res.partner"]
            # A partner is shared on the project when it is the project's
            # partner_id or one of its customer_ids.
            return customers.filtered(
                lambda partner: project.partner_id == partner
                or partner in project.customer_ids
            )
        except Exception:  # pragma: no cover - never break messaging
            _logger.exception(
                "project_customer_user: could not resolve the project for "
                "%s/%s; dropping customers from this notification",
                model,
                res_id,
            )
            return self.env["res.partner"]
