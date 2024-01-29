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
    'name': 'Project: IT Assets',
    'version': '17.0.0.0.1',
    'summary': 'Setup a link for your online meeting.',
    'category': 'Productivity',
    'description': """
        Flow between project and event.
    """,
    'sequence': '280',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_store',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    # Any module necessary for this one to work correctly
    'depends': ['base', 'account_asset'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/it_asset_view.xml',
        'views/res_partner_view.xml',
    ],
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
