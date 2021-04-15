# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Chart',
    'category': 'Project',
    'version': '13.0.1.1.0',
    'description':
        """
Chart Widget for Projects and Tasks
=====================================
This module extend the project form with a chart.
        """,
    'depends': ['project'],
    'auto_install': True,
    'data': [
        # 'views/project_templates.xml',
        'views/assets.xml',
        'views/project_view.xml'
    ],
    'qweb': [
        'static/src/xml/project_task_chart.xml',
    ]
}
