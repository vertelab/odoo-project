from odoo import models, fields, _, api, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class ProjectTask(models.Model):
    _inherit = 'project.task'

    year = fields.Integer(string="Year")
    week = fields.Integer(string="Week")

    @api.constrains('year', 'week')
    def _check_year(self):
        for _rec in self:
            if _rec.week > 52 or _rec.week <= 0:
                raise ValidationError(_('Enter week between 1-52.'))
            if _rec.week and _rec.year <= 0:
                raise ValidationError(_('Please enter a year.'))
            if _rec.year and _rec.week <= 0:
                raise ValidationError(_('Please enter a week.'))

    @api.depends('year', 'week')
    def _compute_year_week(self):
        for _rec in self:
            current_week = int(datetime.today().strftime("%V"))
            current_year = datetime.today().strftime("%y")
            print(range(current_week, 4))
            if _rec.year and _rec.week:
                _rec.year_week = f"{_rec.year}-{_rec.week}"
            else:
                _rec.year_week = False

    @api.model
    def _read_group_year_week(self, stages, domain, order):
        current_year = datetime.today().strftime("%y")

        # last week
        last_week = date.today() + relativedelta(weeks=-1)
        domain = [f"{current_year}-{last_week.strftime('%V')}"]

        # current week
        domain += [f"{current_year}-{date.today().strftime('%V')}"]

        # week 1 after current week
        domain += [
            f"{(date.today() + relativedelta(weeks=+1)).strftime('%y')}"
            f"-{(date.today() + relativedelta(weeks=+1)).strftime('%V')}"
        ]
        domain += [
            f"{(date.today() + relativedelta(weeks=+2)).strftime('%y')}"
            f"-{(date.today() + relativedelta(weeks=+2)).strftime('%V')}"
        ]
        domain += [
            f"{(date.today() + relativedelta(weeks=+3)).strftime('%y')}"
            f"-{(date.today() + relativedelta(weeks=+3)).strftime('%V')}"
        ]
        domain += [
            f"{(date.today() + relativedelta(weeks=+4)).strftime('%y')}-"
            f"{(date.today() + relativedelta(weeks=+4)).strftime('%V')}"
        ]

        return domain

    year_week = fields.Char(string="YY-WW", store=True, compute=_compute_year_week, group_expand='_read_group_year_week')


