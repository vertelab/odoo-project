from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class ProjectTask(models.Model):
    _inherit = 'project.task'

    week = fields.Char(string="Week", group_expand='_read_group_year_week')

    @api.constrains('week')
    def _check_year(self):
        for _rec in self:
            try:
                if isinstance(_rec.week , str) and (int(_rec.week) > 53 or int(_rec.week) < 1):
                    raise ValidationError(_('Enter week between 1-53 or leave blank.'))
            except ValueError:
                raise ValidationError(_('Enter week between 1-53 or leave blank.'))

    @api.onchange('week')
    def _zeropad_week(self):
        for _rec in self:
            if _rec.week:
                _rec.week = _rec.week.zfill(2)

    @api.model
    def _read_group_year_week(self, stages, domain, order):

        # last week
        last_week = date.today() + relativedelta(weeks=-1)
        domain = [last_week.strftime('%V')]

        # current week
        domain += [f"{date.today().strftime('%V')}"]

        # week 1 after current week
        domain += [
            f"{(date.today() + relativedelta(weeks=+1)).strftime('%V')}"
        ]
        domain += [
            f"{(date.today() + relativedelta(weeks=+2)).strftime('%V')}"
        ]
        domain += [
            f"{(date.today() + relativedelta(weeks=+3)).strftime('%V')}"
        ]
        domain += [
            f"{(date.today() + relativedelta(weeks=+4)).strftime('%V')}"
        ]

        return domain

    @api.onchange('week')
    def current_week(self):
        for rec in self:
            if rec.week:
                rec.active_week = datetime.strptime('%s-%s-%s' % (date.today().year, rec.week, 1), '%G-%V-%u').strftime('%Y-%m-%d')
            else:
                rec.active_week = False

    active_week = fields.Char(string="Active Week", related='computed_active_week', store=True)

    @api.depends('week')
    def _compute_current_week(self):
        for rec in self:
            if rec.week:
                rec.computed_active_week = datetime.strptime('%s-%s-%s' % (date.today().year, rec.week, 1), '%G-%V-%u').strftime('%Y-%m-%d')
            else:
                rec.computed_active_week = False
    
    computed_active_week = fields.Char(string="Active Week", compute=_compute_current_week)


