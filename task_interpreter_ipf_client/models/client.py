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

    def is_params_set(self):
        return all([self.get_environment(),
                   self.get_server_url(),
                   self.get_client_secret(),
                   self.get_client_id()])

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

    def get_request(self, url, params=None, payload=None, method="GET"):
        _logger.debug(f'Params:\n{params}')
        _logger.debug(f'Payload:\n{payload}')
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
            params=querystring,
            payload=payload
        )
        return response

    @api.model
    def get_api(self):
        return self

    def post_tolkbokningar(self, activity):
        def format_msg(msg, indent=0):
            out = []
            space = '&nbsp'*4*indent
            for key, value in msg.items():
                if isinstance(value, dict):
                    out.append(f'{space}{key}:<br>')
                    out.append(format_msg(value, indent+1))
                else:
                    out.append(f'{space}{key}: {value}<br>')
            return ''.join(out)
        payload = activity.preprocessing_activity_data(activity)
        msg = _('Interpreter Booking made:')
        message_id = self.env['mail.message'].create({
            'body': (f"{msg}<br>{format_msg(payload)}"),
            'subject': "post_tolkbokningar",
            'author_id': self.env['res.users'].browse(
                self.env.uid).partner_id.id,
            'res_id': activity.res_id,
            'model': activity.res_model,
            })
        _logger.debug(payload)
        _logger.debug('post_tolk: %s' % {
            'body': message_id.body,
            'subject': message_id.subject,
            'author_id': message_id.author_id,
            'res_id': message_id.res_id,
            'model': message_id.model,
            })

        return self.get_request('/tolkportalen-tolkbokning/v1/tolkbokningar',
                                payload=json.dumps(payload),
                                method='POST'), payload

    def get_tolksprak(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/tolksprak')

    def get_kon(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/kon')

    def get_tolktyp(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/tolktyp')

    def get_distanstolktyp(self):
        return self.get_request('/tolkportalen-tolkbokning/v1/distanstolktyp')

    def get_tolkbokningar_id(self, obj_id, kanr):
        return self.get_request(
            f'/tolkportalen-tolkbokning/v1/tolkbokningar/{obj_id}',
            {'kanr': kanr})

    def put_tolkbokningar_id_inleverera(
            self, obj_id, params=None, payload=None):
        return self.get_request(
            f'/tolkportalen-tolkbokning/v1/tolkbokningar/{obj_id}/inleverera',
            params,
            payload,
            'PUT')

    @api.model
    def populate_all_data(self, silent=False):
        if not (self.is_params_set() or silent):
            raise Warning('All parameters are not set in config')
        ok = True
        for method, name, fields in (
                (self.get_tolksprak, 'res.interpreter.language',
                 (('name', 'namn'), ('code', 'id'))),
                (self.get_kon, 'res.interpreter.gender_preference',
                 (('name', 'namn'), ('code', 'id'))),
                (self.get_tolktyp, 'res.interpreter.type',
                 (('name', 'namn'), ('code', 'id'))),
                (self.get_distanstolktyp, 'res.interpreter.remote_type',
                 (('name', 'namn'), ('code', 'id')))
                ):

            if not self._populate_data(method, name, fields):
                msg = f'Failed to populate data for {name}'
                _logger.warn(msg)
                if not silent:
                    raise Warning(msg)
                ok = False
        return ok

    @api.model
    def _populate_data(self, method, model_name, fields):
        result = method()
        if result.status_code not in (200, 201):
            _logger.warn(f'Failed to populate {model_name} with code: '
                         f'{result.status_code} and message: {result.text}')
            return False
        self.env[model_name].search([]).unlink()
        for entry in json.loads(result.text):
            self.env[model_name].create(
                {field_name: entry[result_name] for field_name, result_name in
                 fields})
        return True

    def populate_res_intepreter_language(self):
        self._populate_data(self.get_tolksprak,
                            'res.interpreter.language',
                            (('name', 'namn'), ('code', 'id')))

    def populate_res_interpreter_gender_preference(self):
        self._populate_data(self.get_kon,
                            'res.interpreter.gender_preference',
                            (('name', 'namn'), ('code', 'id')))

    def populate_res_interpreter_remote_type(self):
        self._populate_data(self.get_distanstolktyp,
                            'res.interpreter.remote_type',
                            (('name', 'namn'), ('code', 'id')))

    def populate_res_interpreter_type(self):
        self._populate_data(self.get_tolktyp,
                            'res.interpreter.type',
                            (('name', 'namn'), ('code', 'id')))

    def populate_interpreter_data_cronjob(self):
        if self.is_params_set():
            self.populate_all_data(silent=True)

    def populate_language_cronjob(self):
        if self.is_params_set():
            self.populate_res_intepreter_language()
