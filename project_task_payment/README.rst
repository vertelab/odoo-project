====================
Project: Task Payment
====================

Employees can get money for complaints. This module lets you create a payment
directly from a task, for the person who should be compensated.

Configuration
=============

1. Go to *Project > Configuration > Task Stages*.
2. Open the stage at which the payment button should appear.
3. Enable **Create Payment**.

The flag lives on ``project.task.type``, and task stages are **shared between
projects**. Enabling it on a stage therefore shows the button on every task
that reaches that stage, in every project using it. Create a dedicated stage if
you need the button in one project only.

Usage
=====

On a task whose stage has the flag set:

* Set **Payment Recipient** to the person who should receive the money. This is
  deliberately *not* the task's customer field (``partner_id``) — the customer
  is the one who pays, the recipient is the one who gets paid.
* Click **Create Payment**. A payment form opens, pre-filled with the task, the
  recipient, the memo, and the outbound/supplier direction. Confirm it, and the
  payment is registered on the task.
* Once the task has payments, the button opens the list of them instead, and a
  **Payments** stat button appears on the task.

The button is only visible to users in the **Invoicing** group
(``account.group_account_invoice``), because that is the group Odoo core
requires in order to create an ``account.payment``. Users without it get a
clear error message if they reach the action by another route.

Design notes
============

* **No ``security/ir.model.access.csv``.** The module creates no new models; it
  only adds fields to ``project.task``, ``project.task.type`` and
  ``account.payment``. Shipping our own ACL rows would duplicate — and could
  inadvertently widen — the core ACLs. The button is restricted by group
  instead, and ``action_create_payment`` re-checks the group defensively.
* **``show_payment_button`` is not stored.** It is only read by ``invisible``
  expressions in views, never searched or grouped, so a non-stored compute
  always reflects the current stage configuration and cannot go stale when the
  flag is toggled on a stage.
* **``account.payment.register`` is not used.** That wizard only accepts
  ``account.move`` / ``account.move.line`` as its active model and raises a
  ``UserError`` otherwise, so it cannot drive a payment from a task. The module
  opens an ``account.payment`` form directly instead, with the right context
  defaults.
* **Direction defaults matter.** ``account.payment`` defaults to
  ``payment_type='inbound'`` / ``partner_type='customer'`` ("Receive money").
  A task payment is money paid *out*, so the action sets ``outbound`` and
  ``supplier`` explicitly.

Tests
=====

``tests/test_task_payment.py`` covers the stage flag, the missing-recipient
error, the action contract (model, views, target, context), and the link
between payment and task.

Run them with::

    checkmodule -d <database> -m project_task_payment -t
