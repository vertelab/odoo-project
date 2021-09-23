##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project Task Calendar',
    'version': '14.0.0.0.1',
    'category': '',
    'summary': 'Ties project tasks to the calendar',
    'description': """
        Project tasks that have a date_deadline set will appear in the calendar for the assigned user.\n\n
        Features:\n
            * Creates a calendar post when date_deadline is set.\n
            * Updates the calendar post if the assigned user is changed.\n
            * Removes the calendar post when the project task is deleted.\n\n
        This module is maintained from: https://github.com/vertelab/odoo-project/tree/14.0/project_task_calendar/ \n
""",
    'author': "Vertel AB",
    'license': "AGPL-3",
    'website': 'https://www.vertel.se',
    'depends': ['project','calendar'],
    'data': [],
    'installable': True,
}
