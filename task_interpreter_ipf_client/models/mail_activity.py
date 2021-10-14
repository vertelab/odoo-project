# -*- coding: UTF-8 -*-

###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import datetime
import logging
import pytz

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @staticmethod
    def change_tz(date: datetime.datetime,
                  tz_from: str = 'Europe/Stockholm',
                  tz_to: str = 'utc') -> datetime:
        """
        Convert naive datetime from one tz to another tz while keeping
        it naive.
        """
        # Make sure that we got a date and not None or False as its the
        # default value of some fields.
        if date:
            tz_from = pytz.timezone(tz_from)
            tz_to = pytz.timezone(tz_to)
            return tz_from.localize(date).astimezone(tz_to).replace(tzinfo=None)
        return False

    @api.model
    def preprocessing_activity_data(self, mail_activity):
        perf_op = mail_activity.get_outplacement_value(
            'performing_operation_id')
        payload = {
            'tolkTypId': int(mail_activity.interpreter_type.code),
            'fromDatumTid':
                self.change_tz(
                    mail_activity.time_start, 'utc', 'Europe/Stockholm').strftime(
                    '%Y-%m-%dT%H:%M:00'),
            'tomDatumTid':
                self.change_tz(
                    mail_activity.time_end, 'utc', 'Europe/Stockholm').strftime(
                    '%Y-%m-%dT%H:%M:00'),
            'tolksprakId': mail_activity.interpreter_language.code,
            'tolkkonId': int(mail_activity.interpreter_gender_preference.code) if \
                mail_activity.interpreter_gender_preference and mail_activity.interpreter_gender_preference.code else 1,
            'bestallandeKANr': int(perf_op.ka_nr),
            'adressat': mail_activity.interpreter_receiver or '',
            'adress': {
                'gatuadress': mail_activity.street or '',
                'postnr': mail_activity.zip or '',
                'ort': mail_activity.city or '',
            },
        }
        distanstolkTypId = mail_activity.interpreter_remote_type.code
        if distanstolkTypId:
            payload['distanstolkTypId'] = int(distanstolkTypId)
        return payload
