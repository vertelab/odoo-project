from odoo import models

import traceback
import logging
_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'

    #allow_subtasks = fields.Boolean(tracking=True)

    def write(self, vals):
        if 'allow_subtasks' in vals:
            prefix = "CHANGING_SUBTASKS:"
            _logger.warning(f"{prefix} {vals=}")
            for project in self:
                previous = getattr(project, "allow_subtasks", "undefined")
                new = vals.get('allow_subtasks')
                _logger.warning(f"{prefix} for {project.id=} from {previous} to {new}")
            _logger.warning(prefix + "".join(traceback.format_stack()).replace("\n", "\n" + prefix))
        return super(Project, self).write(vals)


