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

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, models, _

_logger = logging.getLogger(__name__)


class ClientConfig(models.AbstractModel):
    _name = 'ipf.interpreter.client'
    _description = 'Task Interpreter IPF client'

    @api.model
    def get_environment(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "api_ipf.environment", "U1")

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

    @api.model
    def get_system_id(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "api_ipf.ipf_system_id")

    def _is_params_set(self):
        return all[self.get_environment(),
                   self.get_server_url(),
                   self.get_client_secret(),
                   self.get_client_id()]

    def request_call(self, method, url, payload=None,
                     headers=None, params=None):

        response = requests.request(
            method=method,
            url=url,
            data=payload,
            headers=headers,
            params=params,
            verify=False
        )

        return response

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {
            'Content-Type': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': self.get_system_id() or "AFDAFA",
            'AF-EndUserId': "*sys*",
            'AF-Environment': self.get_environment(),
        }
        return headers

    def get_url(self, path):
        server_url = self.get_server_url()
        return f'{server_url.strip("/")}/{path.lstrip("/")}'

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
        params = activity.preprocessing_activity_data(activity)
        _logger.warn('post_tolkbokningar: %s' % params)
        self.env['mail.message'].create({
            'body': _("Interprester medssage %s \n" % (params)),
            'subject': "post_tolkbokningar",
            'author_id': self.env['res.users'].browse(
                self.env.uid).partner_id.id,
            'res_id': activity.res_id,
            'model': activity.res_model_id._name,
            })
        _logger.warn('post_tolk: %s' % {
                    'body': _("Interpreter message %s \n" % (params)),
                    'subject': "post_tolkbokningar",
                    'author_id': self.env['res.users'].browse(
                        self.env.uid).partner_id.id,
                    'res_id': activity.res_id,
                    'model': activity.res_model_id.model,
                    })

        return self.get_request(
            '/tolkportalen-tolkbokning/v1/tolkbokningar', params, 'POST')

    def get_tolksprak(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/tolksprak')

    @api.model
    def populate_res_intepreter_language(self):
        result = self.get_tolksprak()
        if result.status_code not in (200, 201):
            _logger.warn('Failed to populate languages with code: '
                         f'{result.status_code} and message: {result.text}')
            return False
        self.env['res.interpreter.language'].search([]).unlink()
        _logger.warn('NILS: ' + str(len(json.loads(result.text))))
        for lang in json.loads(result.text):
            self.env['res.interpreter.language'].create(
                {'name': lang['namn'], 'code': lang['id']})
        return True

    def populate_language_cronjob(self):
        if self._is_params_set():
            self.populate_res_intepreter_language()

    def get_kon(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/kon')

    def get_tolktyp(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/tolktyp')

    def get_distanstolktyp(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/distanstolktyp')

    def get_tolkbokningar_id(self, object_id):
        return self.get_request(
            '/tolkportalen-tolkbokning/v1/tolkbokningar/%s' % object_id)

    def put_tolkbokningar_id_inleverera(self, object_id, params):
        return self.get_request(
            f'/tolkportalen-tolkbokning/v1/tolkbokningar/{object_id}/inleverera', params, 'PUT')  # noqa:E501
