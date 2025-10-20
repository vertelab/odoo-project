# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.project"

    use_default_types = fields.Boolean(string="Use default stages", default=True)

    @api.model_create_multi
    def create(self, values_list):
        res = super(ProjectTask, self).create(values_list)
        for rec in res:
            if rec.use_default_types:
                default_types = self.env["project.task.type"].search(
                    [("is_default", "=", True)]
                )
                default_types_ids = default_types.mapped("id")
                rec.type_ids = [(4, x, 0) for x in default_types_ids]
        return res
