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
    'name': 'Project: Task Calendar (Deprecated Project)',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Ties project tasks to the calendar',
    'category': 'Project',
    'description': """
        Project tasks that have a date_deadline set will appear in the calendar for the assigned user.\n\n
        Features:\n
            * Creates a calendar post when date_deadline is set.\n
            * Updates the calendar post if the assigned user is changed.\n
            * Removes the calendar post when the project task is deleted.\n\n
        This module is maintained from: https://github.com/vertelab/odoo-project/tree/14.0/project_task_calendar/ \n
        
        Deprecated Issues: https://vertel.se/web#id=1841&action=448&active_id=109&model=project.task&view_type=form&cids=1&menu_id=334 \n 
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_task_calendar',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'depends': ['project', 'calendar'],
    'data': ['views/project_task_view.xml'],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
