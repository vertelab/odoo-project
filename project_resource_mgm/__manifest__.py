# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Resource Management',
    'version': '13.0.1.0.0',
    'website': 'https://www.vertelab.com',
    'category': 'Operations/Project',
    'sequence': 10,
    'summary': 'Project Resource Management',
    'depends': [
        'project',
        'project_hr',
    ],
    'description': "Project Resource Management",
    'data': [
        # 'security/ir.model.access.csv',

        # Views
        'views/project_view.xml',
        'wizard/project_resources_wizard_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
