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
    'name': 'Project: Task SWOT',
    'version': '18.0.1.0.0',
    'summary': 'Add SWOT capabilities to a project.',
    'category': 'Productivity',
    'description': '''
Task SWOT
=========

    This module add SWOT (or other four field) capabilities to a project. Tasks get this attribute to position it in a quadrant
            and at project level generate an image

    Features:

        - UI Integration: Extends 4 view(s) in the Odoo interface.
        - Extends Odoo: Builds on project.project, project.task, project.task.quadrant.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_task_swot',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'depends': ['project', "web_widget_mermaid_field"],
    'data': [
        'views/project_project_views.xml',
        'views/project_task_view.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
