# Copyright 2026 Vertel AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Deny layer for Project Customer users.

Why this exists
---------------
The customer must reach the backend (operator decision, 2026-10-03: "vi vill
att det ska vara i backend"). Reaching the backend requires
``base.group_user``: a non-internal user is redirected out of /odoo by
``portal/controllers/web.py``, and even if that is bypassed the JS client dies
because ``web/models/ir_http.py`` only emits ``user_companies`` when
``is_internal_user`` is true.

But ``base.group_user`` carries 460 ACL rows on ledningssystem — the whole
internal surface: ai.*, account.*, hr.*, prd.*, mis.*, product.*, crm.*,
helpdesk.*, and so on. That over-permission is the actual complaint, not the
group itself.

Odoo has no "internal user with a narrow surface" switch, so this module adds
one. Two mechanisms are used together:

1. **ACL mirror** (``models/ir_model_access.py``) — grants the customer the
   ACLs of the project source groups.

2. **Deny layer** (this file) — denies every model that is *not* on the
   whitelist, via one ``ir.rule`` per model with ``domain_force = [(0,'=',1)]``.

Why ir.rule and not ir.model.access
-----------------------------------
``ir.model.access`` rows are ORed across a user's groups. A deny row on the
customer group therefore does nothing while ``base.group_user`` also grants
the model — the grant wins. ``ir.rule`` domains are ANDed, so a deny rule
always wins. This is the only mechanism in Odoo that can subtract from a
group the user also holds.

Why a whitelist and not a blacklist
-----------------------------------
A blacklist ("deny ai.*, account.*, ...") silently permits every model added
by a future module install. That is exactly how the original over-permission
arose. The whitelist inverts it: a new model is denied until someone adds it
here on purpose.

Maintenance
-----------
Add the model name to ``ALLOWED_MODELS``. That is the whole checklist. The
layer re-syncs on install and on every upgrade, so a newly installed module is
denied automatically without human action.

Scope of the deny
-----------------
The rule is created on the *customer group*, so it only affects Project
Customers. Regular internal users are untouched.
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

CUSTOMER_GROUP = "customer_project_user.group_project_customer_user"

# Marker so generated rules are recognisable and removable without touching
# rules a human created by hand.
DENY_PREFIX = "[customer deny] "

# Models a Project Customer is allowed to reach.
#
# Grouped by reason. Everything not listed here is denied, including models
# from modules that do not exist yet.
ALLOWED_MODELS = [
    # --- Project: the customer's actual job -------------------------------
    "project.project",
    "project.task",
    "project.task.type",
    "project.task.stage.personal",
    "project.task.recurrence",
    "project.task.user.rel",
    "project.milestone",
    "project.tags",
    "project.collaborator",
    "project.update",
    "project.project.stage",
    "project.project.stage.stage",
    "project.favorite",
    # --- Project Scrum: sprints coupled to the project --------------------
    "project.scrum.sprint",
    "project.scrum.meeting",
    "project.scrum.actors",
    "project.scrum.tags",
    "project.scrum.test",
    "project.scrum.us",
    "project.scrum.business.process",
    "project.sprint.type",
    "project.task.burndown.chart.report",
    "report.project.task.user",
    # --- Time tracking ----------------------------------------------------
    "account.analytic.line",
    "account.analytic.account",
    "hr.timesheet.attendance.report",
    "hr_timesheet.sheet",
    "hr_timesheet.sheet.line",
    "hr_timesheet.sheet.new.analytic.line",
    # --- Chatter / mail: the customer must be able to comment -------------
    "mail.message",
    "mail.followers",
    "mail.activity",
    "mail.activity.type",
    "mail.activity.plan",
    "mail.activity.schedule",
    "mail.activity.todo.create",
    "mail.notification",
    "mail.tracking.value",
    "mail.alias",
    "mail.template",
    "mail.mail",
    "mail.compose.message",
    "discuss.channel",
    "discuss.channel.member",
    "discuss.channel.rtc.session",
    # --- Base / framework: required for a /odoo session to boot -----------
    "res.users",
    "res.partner",
    "res.company",
    "res.lang",
    "res.currency",
    "res.groups",
    "res.country",
    "res.country.state",
    "res.country.group",
    "res.bank",
    "res.partner.bank",
    "res.partner.category",
    "res.partner.title",
    "res.partner.industry",
    "res.users.settings",
    "res.users.settings.volumes",
    "res.users.apikeys.description",
    "res.users.apikeys.show",
    "res.users.identitycheck",
    "res.partner.autocomplete.sync",
    "ir.ui.menu",
    "ir.ui.view",
    "ir.ui.view.custom",
    "ir.model",
    "ir.model.fields",
    "ir.model.data",
    "ir.model.access",
    "ir.rule",
    "ir.actions.act_window",
    "ir.actions.actions",
    "ir.actions.report",
    "ir.actions.server",
    "ir.filters",
    "ir.config_parameter",
    "ir.attachment",
    "ir.cron",
    "ir.module.module",
    "ir.asset",
    "ir.qweb",
    "ir.ui.icon",
    "ir.exports",
    "ir.exports.line",
    "ir.logging",
    "ir.profile",
    "ir.http",
    # Found by the operator's dashboard test, 2026-10-03. The first whitelist
    # missed these and the backend surfaced it as:
    #
    #   Sorry, Lamine SBIHI (id=513) doesn't have 'read' access to:
    #   - Embedded Actions, Dashboard (ir.embedded.actions: 1)
    #   Blame the following rules:
    #   - [customer deny] ir.embedded.actions
    #
    # ir.embedded.actions is what the dashboard renders; ir.default and
    # ir.sequence are read on nearly every form; ir.model.fields.selection is
    # read whenever a selection field is rendered. None of them carry business
    # data, so denying them only broke the UI.
    "ir.embedded.actions",
    "ir.default",
    "ir.sequence",
    "ir.sequence.date_range",
    "ir.model.fields.selection",
    "ir.module.category",
    "ir.actions.client",
    "ir.actions.act_url",
    "ir.actions.act_window.view",
    "ir.actions.act_window.close",
    "ir.model.constraint",
    "ir.model.relation",
    "ir.model.inherit",
    "ir.property",
    "ir.binary",
    "ir.cache",
    "ir.autovacuum",
    "ir.cron.trigger",
    "ir.module.module.dependency",
    "board.board",
    "spreadsheet.dashboard",
    "spreadsheet.dashboard.group",
    "report.paperformat",
    # mail: the chatter surface. Denying these broke activities, the invite
    # wizard and message subtypes — all reachable from a task form.
    "mail.message.subtype",
    "mail.activity.plan.template",
    "mail.alias.domain",
    "mail.canned.response",
    "mail.guest",
    "mail.resend.message",
    "mail.resend.partner",
    "mail.scheduled.message",
    "mail.template.preview",
    "mail.wizard.invite",
    "base.module.install.request",
    "base.automation",
    "base.automation.trigger",
    "base.import",
    "base_import.import",
    "base_import.mapping",
    "base.language.install",
    "base.language.export",
    "base.module.update",
    "base.update.translations",
    "base.enable.profiler.wizard",
    "bus.bus",
    "bus.presence",
    "web.editor",
    "web.planner",
    # --- Misc required by the above ---------------------------------------
    "uom.uom",
    "uom.category",
    "decimal.precision",
    "report.layout",
    "digest.digest",
    "digest.tip",
    "utm.campaign",
    "utm.medium",
    "utm.source",
    "utm.tag",
    "rating.rating",
    "iap.account",
    "gamification.badge",
    "gamification.badge.user",
    "gamification.challenge",
    "gamification.goal",
    "change.password.wizard",
    "change.password.user",
    "auth_totp.device",
    "auth_totp.wizard",
    "tier.definition",
    "tier.review",
    "spreadsheet.mixin",
    "resource.calendar",
    "resource.resource",
    "resource.calendar.attendance",
    "resource.calendar.leaves",
    # --- Calendar: tasks carry deadlines and planned dates ----------------
    # Denying calendar.event did not work: the stock rule "All Calendar Event
    # for employees" is attached to base.group_user and grants read, and a
    # group deny rule does not subtract from a group the user also holds.
    # Verified on ledningssystem 2026-10-03 — calendar.event still returned
    # 11504 rows with the deny rule in place. Granting the calendar surface is
    # the honest option; the customer sees the company calendar, which is the
    # same exposure a regular project user has.
    "calendar.event",
    "calendar.attendee",
    "calendar.alarm",
    "calendar.alarm_manager",
    "calendar.recurrence",
    "calendar.filters",
    "calendar.popover.delete.wizard",
]


class IrRule(models.Model):
    _inherit = "ir.rule"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @api.model
    def _deny_customer_group(self):
        return self.env.ref(CUSTOMER_GROUP, raise_if_not_found=False)

    @api.model
    def _deny_models_to_cover(self, customer_group):
        """Every model the customer group can currently reach, minus the
        whitelist.

        Derived from the ACLs the customer group holds (own + mirrored +
        inherited), so the deny layer follows the ACL set rather than a
        hand-maintained model list.
        """
        access = self.env["ir.model.access"].sudo().search(
            [
                "|",
                ("group_id", "=", customer_group.id),
                ("group_id", "in", customer_group.trans_implied_ids.ids),
            ]
        )
        reachable = {row.model_id.model for row in access if row.model_id}
        return sorted(reachable - set(ALLOWED_MODELS))

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    @api.model
    def _deny_sync_customer_rules(self):
        """Make the deny rules match the whitelist. Idempotent."""
        customer_group = self._deny_customer_group()
        if not customer_group:
            _logger.warning(
                "customer_project_user: customer group not found; "
                "deny layer skipped"
            )
            return

        wanted = self._deny_models_to_cover(customer_group)
        wanted_names = {DENY_PREFIX + model for model in wanted}

        existing = self.sudo().search(
            [
                ("groups", "in", customer_group.id),
                ("name", "like", DENY_PREFIX + "%"),
            ]
        )
        existing_names = set(existing.mapped("name"))

        created = removed = 0

        # Create the missing ones.
        to_create = wanted_names - existing_names
        for name in sorted(to_create):
            model_name = name[len(DENY_PREFIX):]
            model = self.env["ir.model"].sudo().search(
                [("model", "=", model_name)], limit=1
            )
            if not model:
                continue
            # SQL views and abstract models cannot carry a record rule: Odoo
            # raises "Invalid domain" or KeyError when the rule is evaluated
            # against a model with no table (e.g. account.balance,
            # report.project.task.user). They are read-only aggregates, so a
            # deny rule is neither possible nor needed.
            if model_name not in self.env:
                continue
            if not self.env[model_name]._table:
                continue
            self.sudo().create(
                {
                    "name": name,
                    "model_id": model.id,
                    "domain_force": "[(0,'=',1)]",
                    "groups": [(4, customer_group.id)],
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                    "perm_unlink": True,
                }
            )
            created += 1

        # Remove rules whose model is now whitelisted (or gone).
        stale = existing.filtered(lambda r: r.name not in wanted_names)
        if stale:
            removed = len(stale)
            stale.sudo().unlink()

        _logger.info(
            "customer_project_user: deny layer synced "
            "(created=%s removed=%s, allowed=%s denied=%s)",
            created,
            removed,
            len(ALLOWED_MODELS),
            len(wanted),
        )

    @api.model
    def _deny_clear_customer_rules(self):
        """Remove every generated deny rule. Used by the rollback path."""
        customer_group = self._deny_customer_group()
        if not customer_group:
            return 0
        rules = self.sudo().search(
            [
                ("groups", "in", customer_group.id),
                ("name", "like", DENY_PREFIX + "%"),
            ]
        )
        count = len(rules)
        rules.sudo().unlink()
        _logger.info(
            "customer_project_user: deny layer cleared (%s rules)", count
        )
        return count
