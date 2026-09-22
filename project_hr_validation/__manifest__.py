# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project HR Validation",
    "summary": """
        Project HR Validation
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://vertel.se/apps/odoo-project/project_hr_validation",
    "depends": ['hr', 'project_purchase'],
    "data": [
        'views/project_project_views.xml',
        'views/purchase_order_views.xml',
    ],
}