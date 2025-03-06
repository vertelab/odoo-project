
import logging
from odoo import api, Command, fields, models, _
_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = "project.project"

    def _get_swot_diagram(self):
        tasks = '\n'.join([f"{t-name}: {t.swot}" for t in self.task_ids])
        return f"""quadrantChart
  x-axis {self.x_axis}
  y-axis {self.y_axis}
  quadrant-1 {self.x_low}
  quadrant-2 {self.x_high}
  quadrant-3 {self.y_low}
  quadrant-4 {self.y_high}
  {tasks}
"""

    swot_diagram = fields.Text(string='SWOT Diagram', compute='_get_mermaid_diagram')

    x_axis = fields.Html(string='X Axis', default="Positive --> Negative", help="The text for X axix, use '-->' as delimiter")
    y_axis = fields.Html(string='Y Axis', default="External --> Internal", help="The text for Y axix, use '-->' as delimiter")
    x_low = fields.Char(string='X Low', default="Opportunities", help="Quadrat 1.1 Opportunities")
    x_high = fields.Char(string='X High', default="Threats", help="Quadrat 1.2 Threats")
    y_high = fields.Char(string='Y High', default="Opportunities", help="Quadrat 2.2 Weakness")
    y_low = fields.Char(string='Y Low', default="Strengths", help="Quadrat 2.1 Opportunities")




from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class Task(models.Model):
    _inherit = "project.task"

    number = fields.Char("Number", default=lambda self: _('New'),
                     copy=False, readonly=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number', _('New')) == _('New'):
                vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        # ~ if 'number' not in vals:
        if True:
            for record in self:
                if record.number == _('New'):
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
        return super().write(vals)
