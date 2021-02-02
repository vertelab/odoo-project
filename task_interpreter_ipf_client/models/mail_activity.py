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

from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model
    def preprocessing_activity_data(self, mail_activity):
        return {
            'tolkbokning': {
                'distanstolkTypId': mail_activity.location_type,
                'fromDatumTid': str(mail_activity.time_start),
                'tomDatumTid': str(mail_activity.time_end),
                'tolksprakId': mail_activity.interpreter_language,
                'tolkkonId': mail_activity.interpreter_gender_preference,
                'bestallandeKAnr': (mail_activity.department_id and
                                    mail_activity.department_id.ka_ref or
                                    None),
                'adress': {
                    'adress': mail_activity.street,
                    'gatuadress': mail_activity.street2,
                    'postnr': mail_activity.zip,
                    'ort': mail_activity.city,
                    'adressat': 'ipsum',
                },
            },
        }
