from odoo import models, api, fields


class Project(models.Model):
    _inherit = 'project.project'

    store_id = fields.Many2one('res.partner', string="Store")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # store_id = fields.Many2one('res.partner', string="Store")