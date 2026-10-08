# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel Sverige AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Project: Task Payment',
    'version': '18.0.1.1.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. 1 = Minor (new features). 0 = Bug fixes
    'summary': "Create a payment from a task, for the person who should be compensated.",
    'category': 'Project',
    'author': 'Vertel Sverige AB',
    'website': "https://vertel.se/apps/odoo-project/project_task_payment",
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'description': '''
Task Payment
============

Employees can get money for complaints. This module adds a *Create Payment*
button to tasks that have reached a stage flagged with **Create Payment**, and
registers the resulting payment on the task.

Features
--------

* A **Create Payment** boolean on task stages (``project.task.type``).
* A **Payment Recipient** field on the task, holding the person who should
  receive the money — deliberately separate from the task's customer.
* A **Create Payment** button in both the task form and the kanban card,
  visible only on flagged stages and only for users with the *Invoicing* group.
* A **Payments** stat button and notebook page listing the payments already
  created for the task.
* The **Task** is shown on the payment form, so the payment can be traced back.

Notes
-----

Task stages are shared between projects. Flagging a stage therefore enables the
button on every task that reaches that stage, in every project using it.

No security rules are shipped: the module only adds fields to existing models,
and the button is restricted through ``account.group_account_invoice``, which is
the group required by Odoo core to create an ``account.payment``.
    ''',
    'depends': ['project', 'account'],
    'data': [
        'views/create_payment.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
