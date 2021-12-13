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
            if int(_rec.week) > 52 or int(_rec.week) <= 0:
                raise ValidationError(_('Enter week between 1-52.'))

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


