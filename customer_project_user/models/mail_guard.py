# Copyright 2026 Vertel AB (<https://vertel.se>).
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

CUSTOMER_GROUP = "customer_project_user.group_project_customer_user"

# Models whose threads a customer is allowed to be part of. Everything else is
# an internal thread and must not reach a customer.
CUSTOMER_VISIBLE_MODELS = (
    "project.project",
    "project.task",
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
        """Remove customers from recipients unless the thread is theirs."""
        model = msg_vals.get("model") or (msg_vals.get("res_id") and self.model)
        if model in CUSTOMER_VISIBLE_MODELS:
            # A project or task thread: customers belong here.
            return partners
        customer_partners = self.env["res.users"].sudo().search(
            [("groups_id", "in", self.env.ref(CUSTOMER_GROUP).id)]
        ).mapped("partner_id")
        if not customer_partners:
            return partners
        dropped = partners & customer_partners
        if dropped:
            _logger.info(
                "customer_project_user: dropped %s Project Customer(s) from "
                "notifications on %s: %s",
                len(dropped),
                model or "unknown model",
                ", ".join(dropped.mapped("email") or dropped.mapped("name")),
            )
        return partners - customer_partners
