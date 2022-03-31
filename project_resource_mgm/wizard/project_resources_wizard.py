# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectResources(models.TransientModel):
    _name = 'project.resources.wizard'

    name = fields.Char(
        string='Name'
    )
    copy_from = fields.Selection(
        [
            ('hr.department', 'HR Department'),
            ('project.project', 'Project'),
        ],
        default='hr.department',
        required=True,
        string="Copy From",
    )
    hr_department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
    members_ids = fields.Many2many(
        comodel_name='res.users',
        string='Members',
        compute='_compute_members',
    )
    targeted_project_id = fields.Many2one(
        comodel_name='project.project',
        required=True,
        string='To Project',
    )

    @api.depends('copy_from', 'hr_department_id', 'project_id')
    def _compute_members(self):
        for rec in self:
            if rec.copy_from and (rec.hr_department_id or rec.project_id):
                if rec.copy_from == 'hr.department':
                    model_id = rec.hr_department_id.id
                    self._get_department_users(rec, model_id)
                else:
                    model_id = rec.project_id.id
                    self._get_project_users(rec, model_id)
            else:
                rec.members_ids = False

    def _get_department_users(self, rec, model_id):
        record_id = rec.env[rec.copy_from].search([('id', '=', model_id)])
        emp_ids = record_id.member_ids
        member_ids = emp_ids.mapped('user_id')
        rec.members_ids = [(4, _id.id) for _id in member_ids]

    def _get_project_users(self, rec, model_id):
        record_id = rec.env[rec.copy_from].search([('id', '=', model_id)])
        member_ids = record_id.mapped('project_member_ids')
        rec.members_ids = [(4, _id.id) for _id in member_ids]

    def copy_resources(self):
        if self.targeted_project_id:
            self.targeted_project_id.project_member_ids = [
                (4, _id.id) for _id in self.members_ids]
