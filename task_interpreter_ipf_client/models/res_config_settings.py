# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID  # noqa:F401

_logger = logging.getLogger(__name__)


class IpfConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ipf_server_url = fields.Char(string='Server URL',
                                 config_parameter='api_ipf.server_url')
    ipf_client_secret = fields.Char(string='Client Secret',
                                    config_parameter='api_ipf.client_secret')
    ipf_client_id = fields.Char(string='Client ID',
                                config_parameter='api_ipf.client_id')
    ipf_environment = fields.Selection(selection=[('U1', 'U1'),
                                                  ('I1', 'I1'),
                                                  ('T1', 'IT'),
                                                  ('T2', 'T2'),
                                                  ('PROD', 'PROD'), ],
                                       string='Environment',
                                       default='U1',
                                       required=True,
                                       config_parameter='api_ipf.environment')

    @api.multi
    def update_all_data(self):
        self.env['ipf.interpreter.client'].populate_all_data()

    @api.multi
    def update_languages(self):
        self.env['ipf.interpreter.client'].populate_res_intepreter_language()

    @api.multi
    def update_gender_preference(self):
        self.env['ipf.interpreter.client'].populate_res_interpreter_gender_preference()  # noqa:E501

    @api.multi
    def update_type(self):
        self.env['ipf.interpreter.client'].populate_res_interpreter_type()

    @api.multi
    def update_remote_type(self):
        self.env['ipf.interpreter.client'].populate_res_interpreter_remote_type()  # noqa:E501
