# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo import api, fields, models, tools
from odoo.addons.rating.models.rating import RATING_LIMIT_SATISFIED, RATING_LIMIT_OK, RATING_LIMIT_MIN
from odoo.osv import expression


class RatingMixin(models.AbstractModel):
    _inherit = 'rating.mixin'

    rating_ids = fields.One2many('rating.rating', 'res_id', string='Rating', groups='base.group_user,customer_project_user.group_project_customer_user', domain=lambda self: [('res_model', '=', self._name)], auto_join=True)