{
    'name': 'Project: AI Plan',
    'version': '18.0.1.0.0',
    'summary': 'AI Plan and Use Case fields for project.task',
    'category': 'Project',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_ai_plan',
    'license': 'AGPL-3',
    'depends': ['project', 'project_task_number', 'web_widget_mermaid_field', 'ai_agent_core'],
    'data': [
        'data/ai_coworker_data.xml',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
