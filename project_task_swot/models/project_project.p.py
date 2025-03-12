import logging
from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def create(self, vals):
        record = super(Project, self).create(vals)
        record.create_quadrants()
        return record

    def write(self, vals):
        record = super(Project, self).write(vals)
        self.create_quadrants()
        return record

    def create_quadrants(self):
        for project in self:
            if not self.env['project.task.quadrant'].search(
                    [('project_id', '=', project.id), ('quadrant', '=', 'x_low')]):
                self.env['project.task.quadrant'].create({"project_id": project.id, "quadrant": "x_low"})

            if not self.env['project.task.quadrant'].search(
                    [('project_id', '=', project.id), ('quadrant', '=', 'x_high')]):
                self.env['project.task.quadrant'].create({"project_id": project.id, "quadrant": "x_high"})

            if not self.env['project.task.quadrant'].search(
                    [('project_id', '=', project.id), ('quadrant', '=', 'y_low')]):
                self.env['project.task.quadrant'].create({"project_id": project.id, "quadrant": "y_low"})

            if not self.env['project.task.quadrant'].search(
                    [('project_id', '=', project.id), ('quadrant', '=', 'y_high')]):
                self.env['project.task.quadrant'].create({"project_id": project.id, "quadrant": "y_high"})

    def _get_swot_diagram(self):
        for rec in self:
            task_wt_quadrant = self.task_ids.filtered(lambda x: x.quadrant)
            if task_wt_quadrant:

                tasks = '\n'.join([
                    f"{task.name.replace(':', '')}: {task.coordinate}"
                    for task in self.task_ids.filtered(lambda x: x.quadrant)
                ])

                quadrant_chart = f"""
                    quadrantChart
                        x-axis {self.x_axis}
                        y-axis {self.y_axis}
                        quadrant-1 {self.x_low}
                        quadrant-2 {self.x_high}
                        quadrant-3 {self.y_low}
                        quadrant-4 {self.y_high}
                        {tasks}
                """
                rec.swot_diagram = quadrant_chart
            else:
                rec.swot_diagram = False


    swot_diagram = fields.Text(string='SWOT Diagram', compute=_get_swot_diagram)

    x_axis = fields.Char(
        string='X Axis', default="Positive --> Negative", help="The text for X axis, use '-->' as delimiter")
    y_axis = fields.Char(
        string='Y Axis', default="External --> Internal", help="The text for Y axis, use '-->' as delimiter")

    x_low = fields.Char(string='X Low', default="Opportunities", help="Quadrant 1.1 Opportunities")
    x_high = fields.Char(string='X High', default="Threats", help="Quadrant 1.2 Threats")
    y_low = fields.Char(string='Y Low', default="Strengths", help="Quadrant 2.1 Strengths")
    y_high = fields.Char(string='Y High', default="Weakness", help="Quadrant 2.2 Weakness")




