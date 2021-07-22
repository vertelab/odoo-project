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
    'version': '12.0.1.1.9',
    'category': 'Outplacement',
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    "depends": ['res_interpreter_language',
                'res_interpreter_gender_preference',
                'res_interpreter_type',
                'res_interpreter_remote_type',
                'mail',
                'api_ipf'
                ],
    'data': [
        "security/ir.model.access.csv",
        'views/client_config_views.xml',
        # 'views/res_config_settings_views.xml',
        # Removing from General setting. For now kept in comment if approve then remove
    ],
    'installable': True,
    'images': [
        'static/description/img.png'
    ],
}
