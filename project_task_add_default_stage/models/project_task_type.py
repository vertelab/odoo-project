# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task.type"

    is_default = fields.Boolean(string="Default stage", default=False)

    @api.model
    def projects_add_defaults(self):
        default_types = self.env["project.task.type"].search(
            [("is_default", "=", True)]
        )
        default_types_ids = default_types.mapped("id")
        projects = self.env["project.project"].search_read([("use_default_types", "=", True)], ["id", "type_ids"])
        if default_types:
            for project in projects:
                types_diff = set(default_types_ids).difference(project["type_ids"])
                # Check if the default stages are already present in the project
                # or if some are missing.
                if types_diff:
                    # Find and add the missing ones
                    project_id = self.env["project.project"].browse(project["id"])
                    # Create a (4, id, 0) operation for each mssing type
                    project_id.type_ids = [(4, x, 0) for x in types_diff]
