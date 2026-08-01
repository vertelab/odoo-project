# -*- coding: utf-8 -*-
{
    'name': 'Project: AI Coworkers',
    'version': '18.0.1.0.0',
    'summary': 'Project Task Manager AI-coworker — task-hantering via OpenAI API',
    'category': 'Project',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'ai_agent_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/project_tools.xml',
        'data/project_coworkers.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
