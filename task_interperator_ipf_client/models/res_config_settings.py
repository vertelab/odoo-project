# -*- coding: utf-8 -*-

from odoo import fields, models


class IpfConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ipf_server_url = fields.Char(string='Server URL',
                                 config_parameter='api_ipf.server_url')
    ipf_client_secret = fields.Char(string='Client Secret',
                                    config_parameter='api_ipf.client_secret')
    ipf_client_id = fields.Char(string='Client ID',
                                config_parameter='api_ipf.client_id')
    ipf_environment = fields.Selection(selection=[('u1', 'U1'),
                                                  ('i1', 'I1'),
                                                  ('t1', 'IT'),
                                                  ('t2', 'T2'),
                                                  ('prod', 'PROD'), ],
                                       string='Environment',
                                       default='u1',
                                       required=True,
                                       config_parameter='api_ipf.environment')
