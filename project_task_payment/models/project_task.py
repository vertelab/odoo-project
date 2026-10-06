from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class ProjectStage(models.Model):
    _inherit = 'project.task.type'

    create_payment = fields.Boolean(
        string="Create Payment",
        default=False,
        help="When a task reaches a stage with this flag set, the "
             "'Create Payment' button is shown on the task.",
    )


class ProjectTask(models.Model):
    _inherit = 'project.task'

    payment_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Payment Recipient",
        tracking=True,
        help="Person who should receive the payment for this task. "
             "This is NOT the task's customer (partner_id); it is the "
             "employee or vendor being compensated.",
    )
    show_payment_button = fields.Boolean(
        string="Show Create Payment Button",
        compute='_compute_show_payment_button',
        help="Technical field: True when the task's stage has the "
             "'Create Payment' flag set. Not stored, so it always reflects "
             "the current stage configuration.",
    )
    payment_ids = fields.One2many(
        comodel_name='account.payment',
        inverse_name='task_id',
        string="Payments",
    )
    payment_count = fields.Integer(
        string="Payment Count",
        compute='_compute_payment_count',
    )

    @api.depends('stage_id.create_payment')
    def _compute_show_payment_button(self):
        for task in self:
            task.show_payment_button = bool(task.stage_id.create_payment)

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for task in self:
            task.payment_count = len(task.payment_ids)

    def action_create_payment(self):
        """Open the payment form (or the list of existing payments).

        The action is only valid on a single task and requires the user to
        have the Invoicing group, since creating an ``account.payment``
        requires ``account.group_account_invoice``.
        """
        self.ensure_one()

        if not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_(
                "You do not have the rights to create payments. "
                "Please ask your administrator to grant you the "
                "'Invoicing' group."
            ))

        action = {
            'name': _('Create Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
        }

        if self.payment_ids:
            action.update({
                'view_mode': 'list,form',
                'domain': [('task_id', '=', self.id)],
                'context': {'default_task_id': self.id},
            })
            return action

        if not self.payment_partner_id:
            raise UserError(_(
                "Please set a payment recipient on the task before "
                "creating a payment."
            ))

        action.update({
            'view_mode': 'form',
            # 'target': 'new' is only honoured by the web client when the
            # first view is a form (see action_service.js).
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_task_id': self.id,
                'default_partner_id': self.payment_partner_id.id,
                # A task payment is money paid OUT to a person, never
                # money received from a customer.
                'default_partner_type': 'supplier',
                'default_payment_type': 'outbound',
                'default_memo': self.name,
            },
        })
        return action


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    task_id = fields.Many2one(
        comodel_name='project.task',
        string="Task",
        ondelete='set null',
        index=True,
        help="Task this payment compensates.",
    )
