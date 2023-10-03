# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2021 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vertel Project Timeline",
    "summary": "Vertel Timeline view for Projects",
    "version": "16.0.1.1.0",
    "category": "Project Management",
    "website": "https://github.com/vertel/odoo-project",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "depends": ["project_timeline", "web_timeline_fix"],
    "data": [
        "views/project_project_view.xml",
        "views/project_task_view.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "vertel_project_timeline/static/src/js/timeline_controller_esm.js",
            "vertel_project_timeline/static/src/js/timeline_model.js"
            # 'vertel_project_timeline/static/src/js/timeline_arch_parser.js',
        ]
    }
}
