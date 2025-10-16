# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2025- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project: Product Requirement Document',
    'version': '1.0',
    'summary': 'A Product Requirements Document (PRD) is a formal document that outlines the purpose, features, and requirements.',
    'category': 'Productivity',
    'description': """
        A Product Requirement Document (PRD), is a central guiding document in product development that describes what a product should do, 
        which needs it should fulfill, and which features it should contain — without specifying how these should be solved technically. 
        The purpose is to ensure that all stakeholders – from product owners and developers to designers and testers – have a shared 
        understanding of the product's goals, functionality, and priorities.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_prd',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'depends': ['mail',
            'web_widget_mermaid_field' # https://github.com/VictorHachard/odoo-modules/tree/17.0/web_widget_mermaid_field,

    ],
    'data': [
        # ~ 'data/cron.xml',
        # ~ 'data/server_action.xml',
        'views/prd_views.xml',
        'views/prd_function_views.xml',
        'views/prd_requirement_views.xml',
        'security/ir.model.access.csv',
        # ~ 'security/prd_security.xml',
    ],
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
