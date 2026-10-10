# -*- coding: utf-8 -*-
{
    'name': 'Project: AI Coworkers',
    'version': '18.0.5.0.0',
    'summary': 'AI coworker for project management — Project (supervisor) + specialist agents.',
    'description': '''
AI Coworkers
============

    AI coworker for project management — Project (supervisor) + specialist agents.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on ai.coworker, ai.coworker.session, project.project, project.task.
        - Agents: Projektanalytiker (domain analysis) + Odoo-utvecklare (implementation).
    ''',
    'category': 'Project',
    'author': 'Vertel Sverige AB',
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
        'data/okf_debug_actions.xml',
        'data/project_tools.xml',
        'data/project_skills.xml',
        'data/project_coworkers.xml',
        'data/project_agents.xml',
        'views/project_task_views.xml',
        'views/session_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
