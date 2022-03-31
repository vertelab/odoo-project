# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Resource Management',
    'summary': 'Project Resource Management',
    'contributor': 'Han Wong <han.wong@vertel.se>',
    'repository': 'git@github.com:vertelab/odoo-project.git',
    'category': 'Operations/Project',
    'version': '14.0.0.0.0',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'description': 'Project Resource Management',
    'sequence': 10,
    'depends': [
        'project',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'wizard/project_resources_wizard_views.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
