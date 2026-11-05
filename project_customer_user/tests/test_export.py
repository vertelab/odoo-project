# -*- coding: utf-8 -*-
"""Project Customer must be able to export.

Operator's report, 2026-11-04: "det finns inte alternativet att exportera" —
a Project Customer had no Export entry in the list cog menu.

Odoo 18 gates the feature on the *group*, in three independent places:

  web/static/src/views/list/list_controller.js
      this.isExportEnable = await user.hasGroup("base.group_allow_export")
  web/static/src/views/list/export_all/export_all.js
      isDisplayed: ... hasGroup("base.group_allow_export")
  models.py:export_data()
      raises UserError unless the user has the group

So the group is the fix. These tests pin the three properties that make that
safe, and the sync that delivers the group to existing customers.

Run with: checkmodule -d <db> -m project_customer_user -t
"""

from odoo.tests import common, tagged

CUSTOMER_GROUP = "project_customer_user.group_project_customer_user"
EXPORT_GROUP = "base.group_allow_export"


@tagged("post_install", "-at_install")
class TestCustomerExport(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_group = cls.env.ref(CUSTOMER_GROUP)
        cls.export_group = cls.env.ref(EXPORT_GROUP)
        cls.user = cls.env["res.users"].create({
            "name": "Exportkund Användare",
            "login": "export.customer@example.com",
            "groups_id": [(6, 0, [cls.customer_group.id])],
        })
        # The customer's own partner is what the record rules match on, so the
        # project must be shared with user.partner_id — not with a separately
        # created partner (they are different records).
        cls.partner = cls.user.partner_id
        cls.project = cls.env["project.project"].create({
            "name": "Exportprojekt",
            "partner_id": cls.partner.id,
            "customer_ids": [(4, cls.partner.id)],
        })
        cls.task = cls.env["project.task"].create({
            "name": "Exporterbar uppgift",
            "project_id": cls.project.id,
        })

    # ------------------------------------------------------------------
    # The group itself
    # ------------------------------------------------------------------

    def test_export_group_is_allowed(self):
        """base.group_allow_export must be on the allow-list."""
        from odoo.addons.project_customer_user.models.res_users_groups import (
            ALLOWED_GROUPS,
        )

        self.assertIn(EXPORT_GROUP, ALLOWED_GROUPS)

    def test_new_customer_gets_the_export_group(self):
        """Creating a customer must grant the group immediately.

        res.users.write() calls _customer_sync_allowed_groups(), so the
        customer does not have to wait for the next registry load.
        """
        self.assertTrue(self.user.has_group(EXPORT_GROUP))

    def test_export_group_implies_nothing(self):
        """The group must stay a pure feature flag.

        If upstream ever makes base.group_allow_export imply another group,
        adding it to ALLOWED_GROUPS could re-open the surface the deny layer
        exists to close. This test is the tripwire.
        """
        self.assertFalse(
            self.export_group.implied_ids,
            "base.group_allow_export now implies %s — review ALLOWED_GROUPS "
            "before shipping" % self.export_group.implied_ids.mapped("display_name"),
        )

    def test_export_group_does_not_imply_internal_user(self):
        """The guard _customer_allowed_group_ids() asserts this for real."""
        base_user = self.env.ref("base.group_user")
        implied = self.export_group.trans_implied_ids if hasattr(
            self.export_group, "trans_implied_ids"
        ) else self.export_group.implied_ids
        self.assertNotIn(
            base_user,
            implied,
            "base.group_allow_export transitively implies base.group_user; "
            "the allow-list guard must be updated",
        )

    # ------------------------------------------------------------------
    # The sync
    # ------------------------------------------------------------------

    def test_sync_grants_missing_group_and_is_idempotent(self):
        """A customer without the group gets it, exactly once."""
        self.user.sudo().with_context(pc_skip_allowed_group_sync=True).write({
            "groups_id": [(3, self.export_group.id)],
        })
        self.user.invalidate_recordset()
        self.assertFalse(self.user.has_group(EXPORT_GROUP))

        changed = self.env["res.users"]._customer_sync_allowed_groups()
        self.user.invalidate_recordset()
        self.assertGreaterEqual(changed, 1)
        self.assertTrue(self.user.has_group(EXPORT_GROUP))

        # Idempotent: nothing missing the second time.
        self.assertEqual(self.env["res.users"]._customer_sync_allowed_groups(), 0)

    def test_sync_never_removes_groups(self):
        """The sync is additive only; removal is the cleanup's job."""
        extra = self.env.ref("base.group_multi_currency")
        self.user.sudo().with_context(pc_skip_allowed_group_sync=True).write({
            "groups_id": [(4, extra.id)],
        })
        self.env["res.users"]._customer_sync_allowed_groups()
        self.user.invalidate_recordset()
        self.assertIn(extra, self.user.groups_id)

    # ------------------------------------------------------------------
    # The payload is still scoped
    # ------------------------------------------------------------------

    def test_export_is_bounded_by_record_rules(self):
        """The customer exports their own project and task — nothing else.

        export_data() runs as the requesting user, so the record rules apply.
        This is why granting the group is not a leak.
        """
        other_user = self.env["res.users"].create({
            "name": "Annan Exportkund",
            "login": "other.customer@example.com",
            "groups_id": [(6, 0, [self.customer_group.id])],
        })
        other_project = self.env["project.project"].create({
            "name": "Annans projekt",
            "partner_id": other_user.partner_id.id,
            "customer_ids": [(4, other_user.partner_id.id)],
        })
        other_task = self.env["project.task"].create({
            "name": "Annans uppgift",
            "project_id": other_project.id,
        })

        customer = self.user.with_user(self.user)
        tasks = customer.env["project.task"].search([])
        self.assertEqual(tasks, self.task)
        self.assertNotIn(other_task, tasks)

        data = tasks.export_data(["name"])
        self.assertEqual(data["datas"], [["Exporterbar uppgift"]])

        # Defence in depth: an explicit search for the other task finds it.
        self.assertFalse(customer.env["project.task"].search([("id", "=", other_task.id)]))
    def test_denied_models_stay_denied_after_the_group_is_added(self):
        """The deny layer still holds for the wide models."""
        customer = self.user.with_user(self.user)
        for model in ("sale.order", "account.move", "hr.employee"):
            if model not in self.env:
                continue
            self.assertEqual(
                customer.env[model].search([]),
                customer.env[model].browse(),
                "%s leaked to the customer" % model,
            )

    def test_export_models_are_whitelisted(self):
        """ir.exports must stay readable, or the export dialog cannot save."""
        from odoo.addons.project_customer_user.models.ir_rule import (
            ALLOWED_MODELS,
        )

        self.assertIn("ir.exports", ALLOWED_MODELS)
        self.assertIn("ir.exports.line", ALLOWED_MODELS)
