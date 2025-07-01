import ast
from datetime import timedelta, datetime
from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from odoo.tools.misc import format_date, get_lang
from odoo.osv.expression import OR
from odoo.addons.mail.models.mail_thread import MailThread


class ProjectProject(models.Model):
    _inherit = "project.project"
    
    customer_ids = fields.Many2many(comodel_name="res.partner", string="Customers")


class NewTask(models.Model):
    _inherit = "project.task"
    
    def _notify_get_groups(self, msg_vals=None):
        """ Handle project users and managers recipients that can assign
        tasks and create new one directly from notification emails. Also give
        access button to portal users and portal customers. If they are notified
        they should probably have access to the document. """
        groups = MailThread._notify_get_groups(self, msg_vals=msg_vals)
        local_msg_vals = dict(msg_vals or {})
        self.ensure_one()

        project_user_group_id = self.env.ref('project.group_project_user').id
        project_manager_group_id = self.env.ref('project.group_project_manager').id

        group_func = lambda pdata: pdata['type'] == 'user' and project_user_group_id in pdata['groups']
        if self.project_id.privacy_visibility == 'followers':
            allowed_user_ids = self.project_id.allowed_internal_user_ids.partner_id.ids
            group_func = lambda pdata:\
                pdata['type'] == 'user'\
                and (
                        project_manager_group_id in pdata['groups']\
                        or (project_user_group_id in pdata['groups'] and pdata['id'] in allowed_user_ids)
                )
        new_group = ('group_project_user', group_func, {})

        if not self.user_id and not self.stage_id.fold:
            take_action = self._notify_get_action_link('assign', **local_msg_vals)
            project_actions = [{'url': take_action, 'title': _('I take it')}]
            new_group[2]['actions'] = project_actions

        groups = [new_group] + groups

        if self.project_id.privacy_visibility == 'portal':
            allowed_user_ids = self.project_id.allowed_portal_user_ids.partner_id.ids
            groups.insert(0, (
                'allowed_portal_users',
                lambda pdata: pdata['type'] == 'portal' and pdata['id'] in allowed_user_ids,
                {}
            ))

        portal_privacy = self.project_id.privacy_visibility == 'portal'
        for group_name, group_method, group_data in groups:
            if group_name in ('customer', 'user') or group_name == 'portal_customer' and not portal_privacy:
                group_data['has_button_access'] = False
            elif group_name == 'portal_customer' and portal_privacy:
                group_data['has_button_access'] = True

        return groups
