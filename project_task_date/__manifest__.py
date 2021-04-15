# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Task Dates',
    'version': '13.0.0.0.1',
    'website': 'https://www.vertelab.com',
    'category': 'Operations/Project',
    'sequence': 10,
    'summary': 'Startdates on task',
    'depends': [
        'project_timeline',
    ],
    'description': "Adds field startdate for tasks on project",
    'data': ['views/project_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
