# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2025- Vertel AB (<https://vertel.se>).
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
    'name': 'Project: Equity Portfolio',
    'version': '18.0.1.0.0',
    'summary': 'Each project of this type is a equity portfolio.',
    'category': 'Productivity',
    'description': '''
Equity Portfolio
================

    A new project type that changes the project to a Equity Porfolio, where each task is an equity.

    Features:

        - Automation: Scheduled jobs: Scheduled Get Latest Equity News, Scheduled Get Latest Equity News.
        - Guided Wizards: Step-by-step dialogs for data entry.
        - UI Integration: Extends 4 view(s) in the Odoo interface.
        - Extends Odoo: Builds on project.equity_research, project.equity_research.topic, project.equity_transaction, project.equity_valuation.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_equity_portfolio',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'depends': ['project','ai_agent' ],
    'data': [
        'data/action_server.xml',
        'data/task_type.xml',
        'security/ir.model.access.csv',
        'wizard/equity_transaction_wizard.xml',
        'views/project_views.xml',
        'views/project_task_views.xml',
    ],
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
