# -*- coding: utf-8 -*-
"""Tests for project_task_payment.

Run with::

    checkmodule -d <database> -m project_task_payment -t

Covers the stage flag, the recipient requirement, the action contract and the
payment/task link.
"""

from odoo.exceptions import UserError
from odoo.tests import common, tagged


@tagged('post_install', '-at_install')
class TestTaskPayment(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.recipient = cls.env['res.partner'].create({'name': 'Recipient'})
        cls.customer = cls.env['res.partner'].create({'name': 'Customer'})
        cls.stage_plain = cls.env['project.task.type'].create({
            'name': 'Plain Stage',
        })
        cls.stage_payment = cls.env['project.task.type'].create({
            'name': 'Payment Stage',
            'create_payment': True,
        })
        cls.project = cls.env['project.project'].create({
            'name': 'Payment Project',
            'partner_id': cls.customer.id,
        })
        # The project's default stage may not be one of ours; set it explicitly.
        cls.task = cls.env['project.task'].create({
            'name': 'Task To Pay',
            'project_id': cls.project.id,
            'stage_id': cls.stage_plain.id,
        })

    # ------------------------------------------------------------------
    # Stage flag → button visibility
    # ------------------------------------------------------------------
    def test_button_hidden_on_plain_stage(self):
        self.assertFalse(self.task.show_payment_button)

    def test_button_shown_on_payment_stage(self):
        self.task.stage_id = self.stage_payment
        self.assertTrue(self.task.show_payment_button)

    def test_toggling_stage_flag_updates_existing_task(self):
        """The compute is not stored, so flipping the stage flag is enough."""
        self.task.stage_id = self.stage_payment
        self.assertTrue(self.task.show_payment_button)
        self.stage_payment.create_payment = False
        self.task.invalidate_recordset(['show_payment_button'])
        self.assertFalse(self.task.show_payment_button)

    # ------------------------------------------------------------------
    # action_create_payment — recipient requirement
    # ------------------------------------------------------------------
    def test_action_requires_recipient(self):
        self.task.stage_id = self.stage_payment
        self.assertFalse(self.task.payment_partner_id)
        with self.assertRaises(UserError):
            self.task.action_create_payment()

    # ------------------------------------------------------------------
    # action_create_payment — action contract
    # ------------------------------------------------------------------
    def test_action_contract(self):
        self.task.stage_id = self.stage_payment
        self.task.payment_partner_id = self.recipient
        action = self.task.action_create_payment()

        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'account.payment')
        self.assertEqual(action['view_mode'], 'form')
        self.assertEqual(action['target'], 'new')
        # target 'new' is only honoured when the first view is a form.
        self.assertEqual(action['views'], [(False, 'form')])

        context = action['context']
        self.assertEqual(context['default_task_id'], self.task.id)
        self.assertEqual(context['default_partner_id'], self.recipient.id)
        # A task payment is money paid out, never money received.
        self.assertEqual(context['default_payment_type'], 'outbound')
        self.assertEqual(context['default_partner_type'], 'supplier')
        self.assertEqual(context['default_memo'], self.task.name)

    def test_action_does_not_use_task_customer(self):
        """The recipient is its own field — the customer must not leak in."""
        self.task.stage_id = self.stage_payment
        self.task.payment_partner_id = self.recipient
        action = self.task.action_create_payment()
        self.assertNotEqual(action['context']['default_partner_id'],
                            self.customer.id)

    # ------------------------------------------------------------------
    # Existing payments → list instead of a new form
    # ------------------------------------------------------------------
    def test_action_lists_existing_payments(self):
        self.task.stage_id = self.stage_payment
        self.task.payment_partner_id = self.recipient
        journal = self.env['account.journal'].search(
            [('type', 'in', ('bank', 'cash')), ('company_id', '=', self.env.company.id)],
            limit=1,
        )
        self.assertTrue(journal, "The test needs at least one bank/cash journal")
        self.env['account.payment'].create({
            'task_id': self.task.id,
            'partner_id': self.recipient.id,
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'journal_id': journal.id,
            'amount': 100.0,
        })
        self.task.invalidate_recordset(['payment_ids', 'payment_count'])
        self.assertEqual(self.task.payment_count, 1)

        action = self.task.action_create_payment()
        self.assertEqual(action['view_mode'], 'list,form')
        self.assertEqual(action['domain'], [('task_id', '=', self.task.id)])
        self.assertNotIn('target', action)

    # ------------------------------------------------------------------
    # Payment ↔ task link
    # ------------------------------------------------------------------
    def test_payment_is_linked_to_task(self):
        self.task.stage_id = self.stage_payment
        self.task.payment_partner_id = self.recipient
        journal = self.env['account.journal'].search(
            [('type', 'in', ('bank', 'cash')), ('company_id', '=', self.env.company.id)],
            limit=1,
        )
        payment = self.env['account.payment'].create({
            'task_id': self.task.id,
            'partner_id': self.recipient.id,
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'journal_id': journal.id,
            'amount': 42.0,
        })
        self.assertEqual(payment.task_id, self.task)
        self.assertIn(payment, self.task.payment_ids)
