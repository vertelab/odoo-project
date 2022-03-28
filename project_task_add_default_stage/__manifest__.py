# -*- coding: utf-8 -*-
{
    "name": "Project Task Stage Defaults",
    "summary": "Adds an option to set default project task stages. These will be applied to all projects.",
    "author": "Vertel AB",
    "contributor": "Daniel Eriksson",
    "maintainer": "Vertel AB",
    "repository": "https://github.com/vertelab/odoo-project",
    "category": "Tools",
    "license": "AGPL-3",
    "version": "14.0.1.1.0",
    "website": "https://vertel.se",
    "description": """
    Adds an option to set default project task stages. These will be applied to all projects.\n
       v14.0.1.1.0 Added option to project weather to use default stages or not.\n
       v14.0.1.0.0 Initial version.\n
       \n
    """,
    "depends": [
        "project",
    ],
    "data": [
        "views/task_type_view.xml",
        "views/project_view.xml",
        "data/add_defaults.xml",
    ],
    "application": False,
    "installable": True,
}
