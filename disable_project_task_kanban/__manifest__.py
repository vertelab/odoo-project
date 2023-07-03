# -*- coding: utf-8 -*-
{
    "name": "Disables Project Task Kanban View",
    "summary": "Opens project.project form view instead of project.task form",
    "author": "Vertel AB",
    "maintainer": "Vertel AB",
    "repository": "https://git.vertel.se/vertelab/odoo-project",
    "category": "Tools",
    "license": "AGPL-3",
    "version": "14.0.3.0.0",
    "website": "https://vertel.se",
    "description": """
        Opens project.project form view instead of project.task form
    """,
    "depends": [
        "project",
    ],
    "data": [
        "views/assets.xml",
    ],
    "application": False,
    "installable": True,
}
