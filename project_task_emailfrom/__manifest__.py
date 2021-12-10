# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2021 Vertel AB (<robin.calvin@vertel.se>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#
# https://www.odoo.com/documentation/14.0/reference/module.html
#
{
    'name': 'Project Task Emailfrom',
    'version': '14.0.1.1.1',
    'summary': 'Exposes the email_from field in project tasks',
    'category': 'Administration',
    'description': """This module exposes the customers (res_partner.email and res_partner.phone) on the  project_task-view. \n
    The module is maintained from: https://github.com/vertelab/odoo-project/ \n
    """,
    'author': 'Vertel AB <robin.calvin@vertel.se>',
    'website': 'https://vertel.se/apps/',
    'license': 'AGPL-3',
    'depends': ['project'],
    'data': ['views/project_view.xml'],
    'demo': [],
    'application': False,
    'installable': True,    
    'auto_install': False,
}
