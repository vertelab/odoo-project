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

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class ClientConfig(models.AbstractModel):
    _name = 'ipf.interpreter.client'
    _description = 'Task Interperator IPF client'

    @api.model
    def get_environment(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "api_ipf.environment", "u1")

    @api.model
    def get_server_url(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "api_ipf.server_url", "http://localhost:8069/v1")

    @api.model
    def get_client_secret(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "api_ipf.client_secret")

    @api.model
    def get_client_id(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "api_ipf.client_id")

    def request_call(self, method, url, payload=None,
                     headers=None, params=None):

        response = requests.request(
            method=method,
            url=url,
            data=payload,
            headers=headers,
            params=params
        )

        return response

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {
            'x-amf-mediaType': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': "AF-SystemId",
            'AF-EndUserId': "AF-EndUserId",
            'AF-Environment': self.get_environment(),
        }
        return headers

    def get_url(self, path):
        server_url = self.get_server_url()
        if server_url[-1] == '/':
            url = server_url[1:]
        else:
            url = server_url
        if path[0] != '/':
            url += '/'
        url += path
        return url

    def get_request(self, url, params=None, method="GET"):
        querystring = {
            "client_secret": self.get_client_secret(),
            "client_id": self.get_client_id()
        }
        if params:
            querystring.update(params)
        url = self.get_url(url)
        response = self.request_call(
            method=method,
            url=url,
            headers=self.get_headers(),
            params=querystring
        )
        return response

    @api.model
    def get_api(self):
        return self


    def post_tolkbokningar(self, activity):
        params = activity.preprocessing_activity_data()
        return self.get_request('/tolkbokningar', params, 'POST')

    def get_tolksprak(self):
        return self.get_request('/tolksprak')

    def get_kon(self):
        return self.get_request('/kon')

    def get_tolktyp(self):
        return self.get_request('/tolktyp')

    def get_distanstolktyp(self):
        return self.get_request('/distanstolktyp')

    def get_tolkbokningar_id(self, object_id):
        return self.get_request('/tolkbokningar/%s' % object_id)

    def put_tolkbokningar_id_inleverera(self, object_id, params):
        return self.get_request(
            '/tolkbokningar/%s/inleverera' % object_id, params, 'PUT')
