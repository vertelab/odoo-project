# -*- coding: utf-8 -*-
{
    'name': 'Project: AI Coworkers',
    'version': '18.0.3.0.1',
    'summary': 'AI coworkers for project management — Task Manager + Project Planner.',
    'description': '''
AI Coworkers
============

    AI coworkers for project management — Task Manager + Project Planner.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on ai.coworker, ai.coworker.session, project.project, project.task.
    ''',
    'category': 'Project',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_ai',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'project_task_number',
        'web_widget_mermaid_field',
        'ai_agent_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/okf_artifact_types_project.xml',
        'data/project_tools.xml',
        'data/project_skills.xml',
        'data/project_coworkers.xml',
        'views/project_task_views.xml',
        'views/session_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
