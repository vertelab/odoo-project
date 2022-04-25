"""Hooks for Changing Menu Group"""
import base64

from odoo import api, SUPERUSER_ID
from odoo.modules import get_module_resource


def test_pre_init_hook(cr):
    """pre init hook"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    menu_item = env['ir.ui.menu'].search([('parent_id', '=', False)])


def test_post_init_hook(cr, registry):
    """post init hook"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    menu_item = env['ir.ui.menu'].search([('parent_id', '=', False)])

    for menu in menu_item:
        if menu.name != 'Project':
            menu.write({
                'groups_id': [(3, env.ref('base.group_user').id)]
            })
            menu.write({
                'groups_id': [(4, env.ref('project_customer_rule.group_advanced_internal').id)]
            })


def test_uninstall_hook(cr, registry):
    """uninstall hook"""

    env = api.Environment(cr, SUPERUSER_ID, {})
    menu_item = env['ir.ui.menu'].search([('parent_id', '=', False)])

    for menu in menu_item:
        if menu.name != 'Project':
            menu.write({
                'groups_id': [(4, env.ref('base.group_user').id)]
            })
