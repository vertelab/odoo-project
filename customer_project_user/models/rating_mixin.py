# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class RatingMixin(models.AbstractModel):
    _inherit = 'rating.mixin'

    rating_ids = fields.One2many('rating.rating', 'res_id', string='Rating', groups='base.group_user,customer_project_user.group_project_customer_user', domain=lambda self: [('res_model', '=', self._name)], auto_join=True)

    rating_last_value = fields.Float('Rating Last Value', groups='base.group_user,customer_project_user.group_project_customer_user', compute='_compute_rating_last_value', compute_sudo=True, store=True)
    rating_last_feedback = fields.Text('Rating Last Feedback', groups='base.group_user,customer_project_user.group_project_customer_user', related='rating_ids.feedback')
    rating_last_image = fields.Binary('Rating Last Image', groups='base.group_user,customer_project_user.group_project_customer_user', related='rating_ids.rating_image')

