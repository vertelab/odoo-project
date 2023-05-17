# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2023- Vertel AB (<https://vertel.se>).
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
    'name': 'Project Task Organizer',
    'version': '14.0',
    'summary': "Seamlessly Customize Task Order in Projects with Odoo 14's Task Organizer Module",
    'category': 'Technical',
    'author': 'Vertel AB',
    'website': "https://vertel.se/apps/odoo-project/project_task_organizer",
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'description': """
    
      * Overview:
        
        Effortlessly rearrange task positions within any project using Odoo 14's Task Organizer module.
        By default, new tasks are added to the top of the column.
        With this module, you gain the flexibility to switch the order of created tasks, placing them at the bottom of the corresponding column.


      * Features:

        - How does it work?
        
          The "Priority field" is associated with every Project Task, with a default setting of "Normal" that can be manually adjusted to "Important." 
          When a Task is designated as "Important," it will be positioned at the top of its respective column, followed by Tasks labeled as "Normal." 
          By default , all newly created Tasks are displayed at the very top of their corresponding Columns and sorted according to their Priority in Kanban View.
          However, this module provides the flexibility to modify this behavior and arrange Tasks to appear at the bottom instead.
      
        - How do I change the default order of my created Tasks?
        
          1.  Navigate to Settings/Project.
          2.  Locate the "Tasks Management" section.
          3.  Within the "Select New Task Order" option, you have full control over Task placement.
        
        - What about the Tree View?
          
          Within the Tree View, this module introduces a convenient feature that enables you to effortlessly rearrange the sequence of your Tasks by simply dragging and dropping them.
          Additionally, a dedicated "Priority Column" will be displayed, featuring a prominent star symbol that signifies the level of importance assigned to each Task.
          It is important to note that while utilizing the "Filters," "Group by," or "Sorting" functionalities, the "drag and drop" capability will be temporarily disabled,
          ensuring the integrity of the selected task arrangement. This will not affect it's current Stage.      
    
    """,
    'depends': ['project'],
    'data': [
      'views/res_config_settings_views.xml',
      'views/task_view.xml',
      ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
