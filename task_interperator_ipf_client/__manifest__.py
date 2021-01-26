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
    'name': 'Outplacement Intepretor IPF Client',
    'version': '12.0.1.0.2',
    'category': 'Outplacement',
    'description': """Implementation of DAFA-IntepreatorBookings integration for REST-calls from the client-module to the server-module.
    (Later from the DAFA-server to the Tolkportalen service.)\n
    v12.0.1.0.2 - added the name Interpretor on several places to differentiate from other modules.\n
    """,

    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
    "depends": ['res_interpreter_language',
                'mail',
    ],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': False,
    'images': [
        'static/description/img.png'
    ],
}
