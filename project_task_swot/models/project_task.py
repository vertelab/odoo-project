# -*- coding: utf-8 -*-


from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class TaskQuadrant(models.Model):
    _name = "project.task.quadrant"


    quadrant = fields.Selection([('x_low', 'x_low'), ('x_high', 'x_high'), ('y_low', 'y_low'), ('y_high', 'y_high')])
    name = fields.Char(compute="get_name_from_project_quadrant")
    project_id = fields.Many2one('project.project')

    def get_name_from_project_quadrant(self):
        for record in self:
            record.name = record.project_id[record.quadrant]


class Task(models.Model):
    _inherit = "project.task"

    is_swot = fields.Boolean(string="Is Swot", related='project_id.is_swot')

    number = fields.Char("Number", default=lambda self: _('New'),
                         copy=False, readonly=True, tracking=True)

    def _read_group_quadrant(self, quadrant, domain):
        project_id = self.env.context.get('default_project_id')

        task_quadrants = self.env['project.task.quadrant'].sudo()._search([
            ('project_id', '=', project_id)])

        return quadrant.browse(task_quadrants)

    quadrant = fields.Many2one(
        'project.task.quadrant', domain="[('project_id','=',project_id)]", group_expand='_read_group_quadrant'
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Your original code
        for vals in vals_list:
            if vals.get('number', _('New')) == _('New'):
                vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')

        # Call super to create the records
        tasks = super(Task, self).create(vals_list)

        # Update coordinates for new tasks in SWOT projects
        swot_tasks = tasks.filtered(lambda t: t.project_id and t.project_id.is_swot and t.quadrant)
        if swot_tasks:
            projects = swot_tasks.mapped('project_id')
            for project in projects:
                project.update_task_coordinates()

        return tasks

    def write(self, vals):
        # Your original code
        if True:
            for record in self:
                if record.number == _('New'):
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')

        # Call super to perform the write
        result = super(Task, self).write(vals)

        # Check if quadrant changed and update coordinates if needed
        if 'quadrant' in vals:
            projects = self.mapped('project_id').filtered(lambda p: p.is_swot)
            for project in projects:
                project.update_task_coordinates()

        return result

    coordinate = fields.Char(string="Coordinate", default="[0.3, 0.6]")

    def action_update_coordinates(self):
        """Button to update coordinates for tasks in the project"""
        for task in self:
            if task.project_id and task.project_id.is_swot:
                task.project_id.update_task_coordinates()
        return True




