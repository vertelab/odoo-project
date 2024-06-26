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
    'name': 'Project: Lawyer',
    'version': '17.0.0.0.1',
    'summary': 'Concflict of interest check and other things.',
    'category': 'Productivity',
    'description': """
        - Check for conflict of interest flag
        - Checkbox Conflict of integrerst done
        - Counterpart
        - Stakeholder_ids
        - Lawyertype project
    """,
    'sequence': '280',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_store',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'depends': ['contacts', 'project', 'privacy_lookup'],
    'data': [
        'views/project_views.xml',
        'wizard/privacy_lookup_wizard_views.xml',
    ],
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
# ~ 'security/ir.model.access.csv',
