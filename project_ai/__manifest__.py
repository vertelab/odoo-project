# -*- coding: utf-8 -*-
{
    'name': 'Project: AI Coworkers',
    'version': '18.0.2.0.0',
    'summary': 'AI coworkers for project management — Task Manager + Project Planner',
    'category': 'Project',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'project_task_number',
        'web_widget_mermaid_field',
        'ai_agent_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/project_tools.xml',
        'data/project_coworkers.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
