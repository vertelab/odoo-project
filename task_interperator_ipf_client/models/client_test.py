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

import json
import logging
from datetime import timedelta
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ClientConfig(models.Model):
    _inherit = 'ipf.interpreter.client'
    _name = 'ipf.interpreter.client.test'
    _description = 'IPF Client Test'
    _rec_name = 'url'

    def _get_default_url(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "mail.catchall.domain", "http://localhost:8069/v1")

    url = fields.Char(string='Url',
                      required=True,
                      default=_get_default_url)
    request_history_ids = fields.One2many('ipf.request.history',
                                          'config_id',
                                          string='Requests')

    def get_url(self, path):
        if self.url[-1] == '/':
            url = self.url[1:]
        else:
            url = self.url
        if path[0] != '/':
            url += '/'
        url += path
        return url

    def request_call(self, method, url, payload=None, headers=None,
                     params=None):
        response = super(ClientConfig, self).request_call(
            method, url, payload, headers, params)
        self.create_request_history(
            method=method,
            url=url,
            response=response,
            payload=payload,
            headers=headers,
            params=params
        )
        return response

    def create_request_history(self, method, url, response, payload=None,
                               headers=None, params=None):
        values = {
            'config_id': self.id,
            'method': method,
            'url': url,
            'payload': payload,
            'request_headers': headers,
            'response_headers': response.headers,
            'params': params,
            'response_code': response.status_code,
        }
        try:
            values.update(message=response.text)
        except json.decoder.JSONDecodeError:
            pass
        self.env['ipf.request.history'].create(values)

    # test functions
    def post_tolkbokningar(self, params):
        data = {
            'tolkbokning': {},
            'tolkbokningId': 2354,
            'bestallandeKAnr': 63,
            'tolkTypId': 643,
            'distanstolkTypId': 663,
            'fromDatumTid': fields.Datetime.now(),
            'tomDatumTid': fields.Datetime.now() + timedelta(days=1),
            'adress': 'New-York',
            'postnr': 457875,
            'ort': 'example',
            'latitud': 45786675,
            'longitud': 45786675,
            'adressat': 'ipsum',
        }
        return self.get_request('/tolkbokningar', params, 'POST')

    def get_tolkbokningar(self, object_id):
        return super(ClientConfig, self).get_tolkbokningar_id('35636')

    def put_tolkbokningar_id_inleverera(self, object_id):
        data = {
            'tolkbokningId': 546456,
            'uppfoljningskategoriKod': '5ert4t6456',
            'kontorsKod': 'wetwjs',
            'projektKod': 'wetwrtjnwjs',
            'uteblivenTolk': 92858,
            'extraMinuter': True,
        }
        return super(ClientConfig, self).put_tolkbokningar_id_inleverera(
            '54765476', data)
