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
#
# https://www.odoo.com/documentation/14.0/reference/module.html

{
    'name': 'Project: Task Emailform',
    'version': '14.0.1.1.1',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Exposes the email_from field in project tasks',
    'category': 'Project',
    'description': """
    This module exposes the customers (res_partner.email and res_partner.phone) on the  project_task-view. \n
    The module is maintained from: https://github.com/vertelab/odoo-project/ \n
    """,
    #'sequence': '1',
    'author': 'Vertel AB <robin.calvin@vertel.se>',
    'website': 'https://vertel.se/apps/odoo-project/project_task_emailform',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'depends': ['project'],
    'data': ['views/project_view.xml'],
    'demo': [],
    'application': False,
    'installable': True,    
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
