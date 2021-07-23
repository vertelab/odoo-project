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

    @api.model
    def preprocessing_activity_data(self, mail_activity):
        def change_tz(timestamp, tz_name='Europe/Stockholm'):
            # Tolk portalen wants timestamps in local swedish time.
            timezone = pytz.timezone(tz_name)
            if not timestamp.tzinfo:
                timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
            return timestamp.astimezone(timezone)

        perf_op = mail_activity.get_outplacement_value(
            'performing_operation_id')
        payload = {
            'tolkTypId': int(mail_activity.interpreter_type.code),
            'fromDatumTid':
                change_tz(mail_activity.time_start).strftime(
                    '%Y-%m-%dT%H:%M:00'),
            'tomDatumTid':
                change_tz(mail_activity.time_end).strftime(
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
