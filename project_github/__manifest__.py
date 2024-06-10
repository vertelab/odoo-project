# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel AB (<https://vertel.se>).
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
    'name': 'Project: Github',
    'version': '14.0',
    'summary': "Creates releations between Github and a projec",
    'category': 'Technical',
    'author': 'Vertel AB',
    'website': "https://vertel.se/apps/odoo-project/project_github",
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'description': """
   Project.project can be a repo, get issues and other things from github.
   Project.task can be an Odoo-module
       
    """,
    'depends': ['project'],
    'external_dependencies': {
        'python': ['PyGithub']
    },
    'data': [
        'views/project_views.xml',
      ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
