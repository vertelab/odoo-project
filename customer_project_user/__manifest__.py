# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2016- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Project Customer User',
    'version': '14.0.0.1.0',
    'summary': 'A user type for project customers',
    'category': 'project',
    'description': """A user type for project customers""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'depends': ['project', 'base', 'hr_timesheet', 'dms', 'contacts', 'portal', 'web', 'project_scrum', 'calendar', 'mail', 'sale_project', 'sale_timesheet'],
    'data': [
        'security/groups.xml',
        'security/project_access.xml',
        'security/mail_access.xml',
        'views/menu.xml'
    ],
    "qweb": [
        'static/src/xml/top_bar.xml',
    ],
    'installable': True,
}
