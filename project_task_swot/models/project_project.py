import re
import math
import random
import logging
from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)


def calculate_coordinates(tasks_by_quadrant, use_positive_only=True):
    """
    Calculate coordinates for tasks grouped by quadrant

    Args:
        tasks_by_quadrant: Dictionary with quadrant type as key and list of tasks as value
        use_positive_only: If True, use only positive coordinates (0 to 1 range)

    Returns:
        Dictionary with task id as key and coordinate string as value
    """
    result = {}

    for quadrant_type, tasks in tasks_by_quadrant.items():
        # Get coordinate ranges for this quadrant
        if use_positive_only:
            x_min, x_max, y_min, y_max = get_positive_quadrant_bounds(quadrant_type)
        else:
            x_min, x_max, y_min, y_max = get_quadrant_bounds(quadrant_type)

        # Calculate coordinates
        coordinates = calculate_task_coordinates(len(tasks), x_min, x_max, y_min, y_max)

        # Assign coordinates to tasks
        for i, task in enumerate(tasks):
            if i < len(coordinates):
                result[task.id] = f"[{coordinates[i][0]:.2f}, {coordinates[i][1]:.2f}]"

    return result


def get_quadrant_bounds(quadrant_type):
    """
    Get coordinate bounds for each quadrant type using -1 to 1 range

    Based on the actual SWOT diagram layout from the images:
    - Top-left: Threats (x_high)
    - Top-right: Opportunities (x_low)
    - Bottom-left: Strengths (y_low)
    - Bottom-right: Weakness (y_high)
    """
    # Add padding to avoid points touching the quadrant borders
    padding = 0.1

    if quadrant_type == 'x_low':  # Opportunities (top-right quadrant)
        return padding, 0.9 - padding, padding, 0.9 - padding
    elif quadrant_type == 'x_high':  # Threats (top-left quadrant)
        return -0.9 + padding, -padding, padding, 0.9 - padding
    elif quadrant_type == 'y_low':  # Strengths (bottom-left quadrant)
        return -0.9 + padding, -padding, -0.9 + padding, -padding
    elif quadrant_type == 'y_high':  # Weakness (bottom-right quadrant)
        return padding, 0.9 - padding, -0.9 + padding, -padding
    else:
        return -0.5, 0.5, -0.5, 0.5  # Default center area


def get_positive_quadrant_bounds(quadrant_type):
    """
    Get coordinate bounds for each quadrant type using 0 to 1 range

    Based on the actual SWOT diagram layout from the images:
    - Top-left: Threats (x_high)
    - Top-right: Opportunities (x_low)
    - Bottom-left: Strengths (y_low)
    - Bottom-right: Weakness (y_high)
    """
    # Add padding to avoid points touching the quadrant borders
    padding = 0.05

    if quadrant_type == 'x_low':  # Opportunities (top-right)
        return 0.55, 0.95, 0.55, 0.95
    elif quadrant_type == 'x_high':  # Threats (top-left)
        return 0.05, 0.45, 0.55, 0.95
    elif quadrant_type == 'y_low':  # Strengths (bottom-left)
        return 0.05, 0.45, 0.05, 0.45
    elif quadrant_type == 'y_high':  # Weakness (bottom-right)
        return 0.55, 0.95, 0.05, 0.45
    else:
        return 0.25, 0.75, 0.25, 0.75  # Default center area


def calculate_task_coordinates(count, x_min, x_max, y_min, y_max):
    """Calculate coordinates for a number of tasks within given bounds"""
    if count == 0:
        return []

    if count == 1:
        # Single task - center of quadrant
        return [((x_min + x_max) / 2, (y_min + y_max) / 2)]

    # Choose distribution method based on number of tasks
    if count <= 5:
        return fixed_position_coordinates(count, x_min, x_max, y_min, y_max)
    elif count <= 15:
        return grid_coordinates(count, x_min, x_max, y_min, y_max)
    else:
        return spiral_coordinates(count, x_min, x_max, y_min, y_max)


def fixed_position_coordinates(count, x_min, x_max, y_min, y_max):
    """Generate coordinates for small numbers of tasks using fixed positions"""
    # Predefined positions for up to 5 tasks
    positions = [
        # Center
        ((x_min + x_max) / 2, (y_min + y_max) / 2),
        # Bottom left
        (x_min + (x_max - x_min) * 0.25, y_min + (y_max - y_min) * 0.25),
        # Top right
        (x_min + (x_max - x_min) * 0.75, y_min + (y_max - y_min) * 0.75),
        # Bottom right
        (x_min + (x_max - x_min) * 0.75, y_min + (y_max - y_min) * 0.25),
        # Top left
        (x_min + (x_max - x_min) * 0.25, y_min + (y_max - y_min) * 0.75),
    ]
    return positions[:count]


def grid_coordinates(count, x_min, x_max, y_min, y_max):
    """Generate coordinates in a grid pattern with slight randomness"""
    coordinates = []

    # Calculate grid dimensions
    grid_size = math.ceil(math.sqrt(count))

    # Calculate cell size
    cell_width = (x_max - x_min) / grid_size
    cell_height = (y_max - y_min) / grid_size

    for i in range(count):
        # Calculate grid position
        row = i // grid_size
        col = i % grid_size

        # Add slight randomness for natural distribution
        jitter = 0.2  # Adjust for more/less randomness
        x = x_min + cell_width * (col + 0.5 + (random.random() - 0.5) * jitter)
        y = y_min + cell_height * (row + 0.5 + (random.random() - 0.5) * jitter)

        # Ensure coordinates stay within bounds
        x = max(x_min, min(x_max, x))
        y = max(y_min, min(y_max, y))

        coordinates.append((x, y))

    return coordinates


def spiral_coordinates(count, x_min, x_max, y_min, y_max):
    """Generate coordinates in a spiral pattern for large numbers of tasks"""
    coordinates = []
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2

    # Calculate available area
    width = x_max - x_min
    height = y_max - y_min
    radius = min(width, height) / 2

    # Number of turns in the spiral
    turns = 3

    for i in range(count):
        # Calculate spiral position
        angle = 2 * math.pi * turns * i / count
        # Normalize distance from center (0 to 1)
        distance = i / count
        # Scale distance to fit within radius
        scaled_distance = distance * radius

        # Convert to Cartesian coordinates
        x = center_x + scaled_distance * math.cos(angle)
        y = center_y + scaled_distance * math.sin(angle)

        # Ensure coordinates stay within bounds
        x = max(x_min, min(x_max, x))
        y = max(y_min, min(y_max, y))

        coordinates.append((x, y))

    return coordinates


class Project(models.Model):
    _inherit = "project.project"

    is_swot = fields.Boolean(string="Is Swot")

    @api.onchange('is_swot')
    def onchange_is_swot(self):
        if not self.is_swot:
            self.env['project.task.quadrant'].search([('project_id', '=', self.id)]).unlink()

    @api.model_create_multi
    def create(self, vals):
        record = super(Project, self).create(vals)
        if record.is_swot:
            record.create_quadrants()
        return record

    def write(self, vals):
        record = super(Project, self).write(vals)
        if vals.get('is_swot'):
            self.create_quadrants()
        elif not vals.get('is_swot'):
            self.env['project.task.quadrant'].search([('project_id', '=', self.id)]).unlink()
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
                    f"{re.sub(
                        r'[^\w\s]',
                        '',
                        task.name.replace('ä', 'a').replace('å', 'a').replace('ö', 'o').replace('Ä', 'A').replace('Å', 'A').replace('Ö', 'O')
                    )}: {task.coordinate}"
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

    def action_view_tasks(self):
        action = super().action_view_tasks()
        if self.is_swot:
            action['context'].update({'search_default_group_by_quadrant': 1})
        return action

    def update_task_coordinates(self):
        """Update coordinates for all tasks in the project"""
        for project in self:
            if not project.is_swot:
                continue

            # Group tasks by quadrant
            tasks_by_quadrant = {}
            for task in project.task_ids.filtered(lambda t: t.quadrant):
                quadrant_type = task.quadrant.quadrant
                if quadrant_type not in tasks_by_quadrant:
                    tasks_by_quadrant[quadrant_type] = []
                tasks_by_quadrant[quadrant_type].append(task)

            # Calculate coordinates for all tasks
            task_coordinates = calculate_coordinates(tasks_by_quadrant, use_positive_only=True)

            # Update task coordinates
            for task_id, coordinate in task_coordinates.items():
                self.env['project.task'].browse(task_id).coordinate = coordinate


