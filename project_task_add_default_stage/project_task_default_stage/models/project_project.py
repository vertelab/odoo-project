# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.project"

    use_default_types = fields.Boolean(string="Use default stages", default=True)

    @api.model
    def create(self, values):
        res = super(ProjectTask, self).create(values)
        if res.use_default_types:
            default_types = self.env["project.task.type"].search(
                [("is_default", "=", True)]
            )
            default_types_ids = default_types.mapped("id")
            res.type_ids = [(4, x, 0) for x in default_types_ids]
        return res
