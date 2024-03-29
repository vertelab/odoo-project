# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_members_count = fields.Integer(
        compute='_compute_project_members',
        string="Project Members",
    )
    project_member_ids = fields.Many2many(
        comodel_name='res.users',
        compute='_compute_project_members',
        inverse='_set_project_members',
        store=True,
        string='Project Members',
    )

    @api.depends('user_id', 'task_ids')
    def _compute_project_members(self):
        for _rec in self:
            ids = []
            if _rec.user_id:
                ids.append(_rec.user_id)
            if _rec.task_ids:
                for task in _rec.task_ids:
                    if task.user_id:
                        ids.append(task.user_id)
            _rec.project_member_ids = [(4, _id.id) for _id in set(ids)]
            _rec.project_members_count = len(_rec.project_member_ids)

    def _set_project_members(self):
        pass

    def action_project_members(self):
        return {
            'name': _('Members of Project'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'views': [(False, 'tree')],
            'view_mode': 'tree',
            'view_id': False,
            'domain': [('id', 'in', self.project_member_ids.ids)],
        }


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_start_date = fields.Date(
        string='Task Start Date',
    )
