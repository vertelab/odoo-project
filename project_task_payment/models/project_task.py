from odoo import models, fields, api

class ProjectStage(models.Model):
    _inherit = 'project.task.type'

    create_payment = fields.Boolean(string="Create Payment", default=False)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    show_payment_button = fields.Boolean(string="Show Create Payment Button",
                                         compute='_compute_show_payment_button',
                                         store=True)
    payment_ids = fields.One2many(comodel_name='account.payment',inverse_name='task_id',string="Payment",help="") # domain|context|auto_join|limit

    @api.depends('stage_id.create_payment')
    def _compute_show_payment_button(self):
        for task in self:
            task.show_payment_button = task.stage_id.create_payment

    def action_create_payment(self):
        if self.payment_ids:
            return {
                'name': 'Create Payment',
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'view_mode': 'list',
                'domain': 
                [('task_id', '=', self.id)],
            }
        else:
            return {
                'name': 'Create Payment',
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_partner_id': self.partner_id.id,
                    'default_task_id': self.id,
                },
            }

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    task_id = fields.Many2one(comodel_name='project.task',string="Task",help="") # domain|context|ondelete="'set null', 'restrict', 'cascade'"|auto_join|delegate
    
    
