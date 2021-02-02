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
    ipf_environment = fields.Selection(selection=[('U1', 'U1'),
                                                  ('I1', 'I1'),
                                                  ('T1', 'T1'),
                                                  ('T2', 'T2'),
                                                  ('PROD', 'PROD'), ],
                                       string='Environment',
                                       default='U1',
                                       required=True,
                                       config_parameter='api_ipf.environment')
