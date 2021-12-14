# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<https://vertel.se>).
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
    "name": "Project Task WeekNo",
    'summary': 'Project Task WeekNo',
    'author': 'Vertel AB',
    'category': 'Project Task WeekNo',
    "version": "14.0.0.0.0",
    'license': 'AGPL-3',
    'website': 'https://vertel.se/',
    "description": """
        Helps to plan the week
    """,
    "depends": [
        "project",
    ],
    "data": [
        "views/project_task_view.xml"
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
