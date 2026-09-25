{
    'name': 'Project Tags Company',
'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-project/project_tags_company',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Add company_id to project.tags.',
    'description': '''
Project Tags Company
====================

    Add company_id to project.tags.

    Features:

        - Extends Odoo: Builds on project.tags.
    ''',
    'depends': ['project'],
    'data': [
        'security/ir_rule.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
