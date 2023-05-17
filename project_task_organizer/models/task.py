from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'
    priority_icon = fields.Char(compute='_compute_priority_icon')

    @api.model
    def create(self, vals):
        
        env = self.env
        IrConfigParameter = env['ir.config_parameter'].sudo()
        order_choice = IrConfigParameter.get_param('task.order', default='')
        
        if order_choice == '2':
            
            # Find the last task in the corresponding column and get its sequence number
            last_task = self.search([('project_id', '=', vals.get('project_id'))], order='sequence desc', limit=1)
            
            last_sequence = last_task.sequence if last_task else 0

            # Set the new task's sequence number to be greater than that of the last task
            vals['sequence'] = last_sequence + 1
        
            # Create the new task with the updated sequence number
        return super(ProjectTask, self).create(vals)
    
    
    def _compute_priority_icon(self):
        star_icon = '<i class="fa fa-star" style="color:gold;"></i>'
        blank_icon = '<i class="fa fa-star" style="color:lightgrey;"></i>'
        for record in self:
            record.priority_icon = star_icon if record.priority == '1' else blank_icon