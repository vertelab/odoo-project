# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
    'name': 'Project: Mis budget',
    'version': '16.0.0.0.1',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Setup a link between budget and projekt/task.',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'description': """
        Flow between project and budget.
    """,
    #'sequence': '1',
    'sequence': '280',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_mis_budget',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    # Any module necessary for this one to work correctly
    'depends': ['mis_builder_budget', 'mis_budget_extended','project',],

    # always loaded
    'data': [
        'views/project_view.xml',
        'views/mis_budget.xml',
        'views/kpi_mis_budget.xml',
    ],
    'application': False,
    "installable": True,
    "auto_install": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
