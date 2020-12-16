# -*- coding: UTF-8 -*-

################################################################################
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
################################################################################

from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model
    def preprocessing_activity_data(self):
        return {
            'tolkbokning': {
                'distanstolkTypId': self.location_type,
                'fromDatumTid': str(self.time_start),
                'tomDatumTid': str(self.time_end),
                'tolksprakId': self.interpreter_language,
                'tolkkonId': self.interpreter_gender_preference,
                'bestallandeKAnr': self.department_id and self.department_id.ka_ref or None,
                'adress': {
                    'adress': self.street,
                    'gatuadress': self.street2,
                    'postnr': self.zip,
                    'ort': self.city,
                    'adressat': 'ipsum',
                },
            },
        }
