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
    'name': 'Project: Customer Project User',
    'version': '14.0.0.1.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'A user type for project customers.',
    'category': 'Project',
    'description': """
    A user type for project customers.
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/customer_project_user',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    # ~ 'depends': ['project', 'base', 'hr_timesheet', 'dms', 'contacts', 'portal', 'web', 'project_scrum', 'calendar', 'mail', 'sale_project', 'sale_timesheet'],
    'depends': ['project', 'base', 'hr_timesheet', 'contacts', 'portal', 'web', 'project_scrum', 'calendar', 'mail', 'sale_project', 'sale_timesheet', 'note'],
    'data': [
        'security/groups.xml',
        'security/project_access.xml',
        'security/mail_access.xml',
        'views/menu.xml',
        'views/project_view.xml',
    ],
    "qweb": [
        'static/src/xml/top_bar.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
