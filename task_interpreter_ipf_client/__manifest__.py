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

{
    'name': 'Outplacement Intepreter IPF Client',
    'version': '12.0.1.1.5',
    'category': 'Outplacement',
    'description': """Implementation of DAFA-IntepreatorBookings integration for REST-calls from the client-module to the server-module.
    (Later from the DAFA-server to the Tolkportalen service.)\n
    v12.0.1.0.2 - added the name Interpretor on several places to differentiate from other modules.\n
    v12.0.1.1.0 - Read field addressat from the UI.
    v12.0.1.1.2 - Minor log message fix
    v12.0.1.1.3 - Translations.
    v12.0.1.1.4 - AFC-2145 Updated Log message when Interpreter activity created.
    v12.0.1.1.5 - AFC-2405 Updated Log message of Interpreter booking creation.
    """,

    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    "depends": ['res_interpreter_language',
                'res_interpreter_gender_preference',
                'res_interpreter_type',
                'res_interpreter_remote_type',
                'mail',
                ],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
        'views/res_config_settings_views.xml',
        ],
    'installable': True,
    'images': [
        'static/description/img.png'
        ],
}
