# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)

PROJECT_TASK_FIELDS = {
    'number'
}

# The field default is the translated string _('New') — 'New' in English,
# 'Ny' in Swedish.  A task that has not yet been assigned a real number
# carries that placeholder, so the unique index must ignore every translation
# of it, not just the English one.
PLACEHOLDER_NUMBERS = ('New', 'Ny')


class Task(models.Model):
    _name = "project.task"
    _inherit = "project.task"

    number = fields.Char("Number", default=lambda self: _('New'),
                     copy=False, readonly=True, tracking=True)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | PROJECT_TASK_FIELDS

    @property
    def SELF_WRITABLE_FIELDS(self):
        return super().SELF_WRITABLE_FIELDS | PROJECT_TASK_FIELDS

    def init(self):
        """Create a partial unique index on ``number``.

        A plain ``unique(number)`` cannot be used: every task that has not yet
        been assigned a number carries the transient placeholder ``New``
        (the field default), so such a constraint would reject the second
        unnumbered task.  The uniqueness only matters for real numbers, hence
        the partial index.  ``_sql_constraints`` cannot express a ``WHERE``
        clause, so the index is created directly.

        The placeholder is translated, so every known translation must be
        excluded.  Measured on ledningssystem 2026-10-03: the table holds 308
        ``'New'`` and 283 ``'Ny'`` rows.  A ``WHERE number <> 'New'`` clause
        leaves the 283 Swedish rows in the index and the CREATE fails on the
        existing duplicates.
        """
        placeholders = ", ".join(
            "'%s'" % value for value in PLACEHOLDER_NUMBERS
        )
        self._cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS project_task_number_uniq
                ON project_task (number)
                WHERE number IS NOT NULL AND number NOT IN (%s)
        """ % placeholders)

    @api.constrains('number')
    def _check_number_unique(self):
        """Refuse a number that is already used by another task.

        The partial unique index is the hard guarantee; this method only turns
        the IntegrityError into a readable message for the user.
        """
        for task in self:
            if not task.number or task.number in PLACEHOLDER_NUMBERS:
                continue
            duplicate = self.search_count([
                ('number', '=', task.number),
                ('id', '!=', task.id),
            ])
            if duplicate:
                raise ValidationError(
                    _('Task number "%s" is already in use by another task.') % task.number)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number', _('New')) == _('New'):
                if not self.env.user._is_portal():
                    vals['number'] = self.env['ir.sequence'].next_by_code('project.task.number') or _('New')
                else:
                    vals['number'] = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if not vals:
            return True
        res = super().write(vals)
        for record in self:
            if record.number == _('New'):
                if not self.env.user._is_portal():
                    record.number = self.env['ir.sequence'].next_by_code('project.task.number') or False
                else:
                    record.number = self.env['ir.sequence'].sudo().next_by_code('project.task.number') or False
        return res
