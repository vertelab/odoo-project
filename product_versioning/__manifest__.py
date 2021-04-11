# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Versioning',
    'version': '13.0.1.1.0',
    'website': 'https://www.vertelab.com',
    'category': 'Operations/Project',
    'sequence': 10,
    'summary': 'Organize and schedule your projects ',
    'depends': [
        'project',
    ],
    'description': """
        Product Versioning
        ====================
        It shall be possible to switch between different versions of project plans.
        
        Certain data shall be the same between all versions of the project plan, for an example time reporting
        
        Other data is unique for for each project plan and therefore needs to be saved with that version
    """,
    'data': [
        'security/ir.model.access.csv',

        # Views
        'views/project_view.xml',
        'views/project_versioning_project_view.xml',
        'views/project_versioning_task_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
