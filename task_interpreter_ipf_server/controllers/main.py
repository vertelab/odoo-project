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

import logging
from datetime import timedelta
from odoo import http, api, fields
from .token import valid_response, invalid_response

_logger = logging.getLogger(__name__)


class IpfReportServer(http.Controller):
    _suffix_url = '/v1'

    @api.model
    def validating_params(self, params, kwargs):
        """Checking params
                 (param[str], required[boolean], type, array[boolean])"""
        missed_required = []
        errors = []
        type_match = {'string': str, 'integer': int}
        for param_prop in params:
            if not kwargs.get(param_prop[0]) and param_prop[1]:
                missed_required.append(param_prop[0])
            elif kwargs.get(param_prop[0]) and param_prop[2]:
                value = kwargs[param_prop[0]]
                if len(param_prop) == 4 and param_prop[3]:
                    values = value.split(',')
                else:
                    values = [value]
                for value in values:
                    try:
                        type_match[param_prop[2]](value)
                    except Exception:
                        message = 'Parameter %s is not %s' % (
                            param_prop[0], param_prop[2])
                        errors.append(message)
                        break
        if missed_required:
            errors.append('Missed required fields')
        return missed_required, errors

    @api.model
    def validating_number(self, field_name, value):
        if not value.isdigit():
            return invalid_response(
                'Bad request', '%s is not number' % field_name, 403)

    @http.route(_suffix_url + "/tolkbokningar", methods=["POST"],
                type="http", auth="none", csrf=False)
    def tolkbokningar(self, *args, **kwargs):
        return valid_response({'tolkbokningId': '456465'})

    @http.route([
        _suffix_url + "/tolkbokningar/<tolkbokningar_id>",
    ],
        methods=["GET"], type="http", auth="none", csrf=False)
    def tolkbokningar_id(self, tolkbokningar_id, **kwargs):
        data = {
            'tolkbokning': {},
            'tolkbokningId': 2354,
            'tekniskStatusTypId': 6,
            'bestallandeKAnr': 63,
            'tolkTypId': 643,
            'distanstolkTypId': 663,
            'fromDatumTid': fields.Datetime.now(),
            'tomDatumTid': fields.Datetime.now() + timedelta(days=1),
            'adress': 'New-York',
            'postnr': 457875,
            'ort': 'example',
            'kommunkod': 'example',
            'lanskod': 457875,
            'latitud': 45786675,
            'longitud': 45786675,
            'adressat': 'ipsum',
        }
        return valid_response(data)

    @http.route(_suffix_url + "/tolkbokningar/<tolkbokningar_id>/inleverera",
                methods=["PUT"], type="http", auth="none", csrf=False)
    def tolkbokningar_inleverera(self, tolkbokningar_id, **kwargs):
        return valid_response()

    @http.route([
        _suffix_url + "/tolksprak",
        _suffix_url + "/kon",
        _suffix_url + "/tolktyp",
        _suffix_url + "/distanstolktyp",
    ],
        methods=["GET"], type="http", auth="none", csrf=False)
    def tolksprak(self, *args, **kwargs):
        data = {
            'tolkspråk': [],
            'kön': [],
            'id': 54344,
            'namn': 'namn',
        }
        return valid_response(data)
