# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from collections import defaultdict

from odoo import _, api, fields, models, modules, tools
from odoo.tools import clean_context, SQL
from odoo.exceptions import AccessError, UserError


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id', string='Followers',
        groups='base.group_user,customer_project_user.group_project_customer_user')
    message_partner_ids = fields.Many2many(
        comodel_name='res.partner', string='Followers (Partners)',
        compute='_compute_message_partner_ids',
        inverse='_inverse_message_partner_ids',
        search='_search_message_partner_ids',
        groups='base.group_user,customer_project_user.group_project_customer_user',
    )
    message_attachment_count = fields.Integer(
        'Attachment Count', compute='_compute_message_attachment_count',
        groups="base.group_user,customer_project_user.group_project_customer_user"
    )


class MailActivity(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    activity_ids = fields.One2many(
        'mail.activity', 'res_id', 'Activities',
        auto_join=True,
        groups="base.group_user,customer_project_user.group_project_customer_user", )
    activity_state = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned')], string='Activity State',
        compute='_compute_activity_state',
        groups="base.group_user,customer_project_user.group_project_customer_user",
        help='Status based on activities\nOverdue: Due date is already passed\n'
             'Today: Activity date is today\nPlanned: Future activities.')
    activity_user_id = fields.Many2one(
        'res.users', 'Responsible User',
        related='activity_ids.user_id', readonly=False,
        search='_search_activity_user_id',
        groups="base.group_user,customer_project_user.group_project_customer_user")
    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Next Activity Type',
        related='activity_ids.activity_type_id', readonly=False,
        search='_search_activity_type_id',
        groups="base.group_user,customer_project_user.group_project_customer_user")
    activity_date_deadline = fields.Date(
        'Next Activity Deadline',
        compute='_compute_activity_date_deadline', search='_search_activity_date_deadline',
        compute_sudo=False, readonly=True, store=True,
        groups="base.group_user,customer_project_user.group_project_customer_user")
    my_activity_date_deadline = fields.Date(
        'My Activity Deadline',
        compute='_compute_my_activity_date_deadline', search='_search_my_activity_date_deadline',
        compute_sudo=False, readonly=True, groups="base.group_user,customer_project_user.group_project_customer_user")
    activity_summary = fields.Char(
        'Next Activity Summary',
        related='activity_ids.summary', readonly=False,
        search='_search_activity_summary',
        groups="base.group_user,customer_project_user.group_project_customer_user", )


class NewMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """ Override that adds specific access rights of mail.message, to remove
        ids uid could not see according to our custom rules. Please refer to
        check_access_rule for more details about those rules.

        Non employees users see only message with subtype (aka do not see
        internal logs).

        After having received ids of a classic search, keep only:
        - if author_id == pid, uid is the author, OR
        - uid belongs to a notified channel, OR
        - uid is in the specified recipients, OR
        - uid has a notification on the message
        - otherwise: remove the id
        """
        # Rules do not apply to administrator
        if self.env.is_superuser():
            return super()._search(domain, offset, limit, order, access_rights_uid)

        # Non-employee see only messages with a subtype and not internal
        if not self.env['res.users'].has_group('base.group_user') or self.env['res.users'].has_group(
                'customer_project_user.group_project_customer_user'):
            domain = self._get_search_domain_share() + domain

        # make the search query with the default rules
        query = super()._search(domain, offset, limit, order, access_rights_uid)

        # retrieve matching records and determine which ones are truly accessible
        self.flush_model(['model', 'res_id', 'author_id', 'message_type', 'partner_ids'])
        self.env['mail.notification'].flush_model(['mail_message_id', 'res_partner_id'])

        pid = self.env.user.partner_id.id
        ids = []
        allowed_ids = set()
        model_ids = defaultdict(lambda: defaultdict(set))

        rel_alias = query.make_alias(self._table, 'partner_ids')
        query.add_join("LEFT JOIN", rel_alias, 'mail_message_res_partner_rel', SQL(
            "%s = %s AND %s = %s",
            SQL.identifier(self._table, 'id'),
            SQL.identifier(rel_alias, 'mail_message_id'),
            SQL.identifier(rel_alias, 'res_partner_id'),
            pid,
        ))
        notif_alias = query.make_alias(self._table, 'notification_ids')
        query.add_join("LEFT JOIN", notif_alias, 'mail_notification', SQL(
            "%s = %s AND %s = %s",
            SQL.identifier(self._table, 'id'),
            SQL.identifier(notif_alias, 'mail_message_id'),
            SQL.identifier(notif_alias, 'res_partner_id'),
            pid,
        ))
        self.env.cr.execute(query.select(
            SQL.identifier(self._table, 'id'),
            SQL.identifier(self._table, 'model'),
            SQL.identifier(self._table, 'res_id'),
            SQL.identifier(self._table, 'author_id'),
            SQL.identifier(self._table, 'message_type'),
            SQL(
                "COALESCE(%s, %s)",
                SQL.identifier(rel_alias, 'res_partner_id'),
                SQL.identifier(notif_alias, 'res_partner_id'),
            ),
        ))
        for id_, model, res_id, author_id, message_type, partner_id in self.env.cr.fetchall():
            ids.append(id_)
            if author_id == pid:
                allowed_ids.add(id_)
            elif partner_id == pid:
                allowed_ids.add(id_)
            elif model and res_id and message_type != 'user_notification':
                model_ids[model][res_id].add(id_)

        allowed_ids.update(self._find_allowed_doc_ids(model_ids))
        allowed = self.browse(id_ for id_ in ids if id_ in allowed_ids)
        return allowed._as_query(order)

    def check_access_rule(self, operation):
        """ Access rules of mail.message:
            - read: if
                - author_id == pid, uid is the author OR
                - create_uid == uid, uid is the creator OR
                - uid is in the recipients (partner_ids) OR
                - uid has been notified (needaction) OR
                - uid have read access to the related document if model, res_id
                - otherwise: raise
            - create: if
                - no model, no res_id (private message) OR
                - pid in message_follower_ids if model, res_id OR
                - uid can read the parent OR
                - uid have write or create access on the related document if model, res_id, OR
                - otherwise: raise
            - write: if
                - author_id == pid, uid is the author, OR
                - uid is in the recipients (partner_ids) OR
                - uid has write or create access on the related document if model, res_id
                - otherwise: raise
            - unlink: if
                - uid has write or create access on the related document
                - otherwise: raise

        Specific case: non employee users see only messages with subtype (aka do
        not see internal logs).
        """
        def _generate_model_record_ids(msg_val, msg_ids):
            """ :param model_record_ids: {'model': {'res_id': (msg_id, msg_id)}, ... }
                :param message_values: {'msg_id': {'model': .., 'res_id': .., 'author_id': ..}}
            """
            model_record_ids = {}
            for id in msg_ids:
                vals = msg_val.get(id, {})
                if vals.get('model') and vals.get('res_id'):
                    model_record_ids.setdefault(vals['model'], set()).add(vals['res_id'])
            return model_record_ids

        if self.env.is_superuser():
            return

        # just in case there are ir.rules
        super().check_access_rule(operation)

        # Non employees see only messages with a subtype (aka, not internal logs)
        if not (self.env['res.users'].has_group('base.group_user') or self.env['res.users'].has_group(
                'customer_project_user.group_project_customer_user')):
            self._cr.execute('''SELECT DISTINCT message.id, message.subtype_id, subtype.internal
                                FROM "%s" AS message
                                LEFT JOIN "mail_message_subtype" as subtype
                                ON message.subtype_id = subtype.id
                                WHERE message.message_type = %%s AND
                                    (message.is_internal IS TRUE OR message.subtype_id IS NULL OR subtype.internal IS TRUE) AND
                                    message.id = ANY (%%s)''' % (self._table), ('comment', self.ids,))
            if self._cr.fetchall():
                raise AccessError(
                    _('The requested operation cannot be completed due to security restrictions. Please contact your '
                      'system administrator.\n\n(Document type: %s, Operation: %s)', self._description, operation)
                    + ' - ({} {}, {} {})'.format(_('Records:'), self.ids[:6], _('User:'), self._uid)
                )

        # Read mail_message.ids to have their values
        message_values = dict((message_id, {}) for message_id in self.ids)

        self.flush_recordset(['model', 'res_id', 'author_id', 'create_uid', 'parent_id', 'message_type', 'partner_ids'])
        self.env['mail.notification'].flush_model(['mail_message_id', 'res_partner_id'])

        if operation == 'read':
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.create_uid,
                                m.parent_id,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_notification" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=self.env.user.partner_id.id, ids=self.ids))
            for mid, rmod, rid, author_id, create_uid, parent_id, partner_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'create_uid': create_uid,
                    'parent_id': parent_id,
                    'notified': any((message_values[mid].get('notified'), partner_id)),
                    'message_type': message_type,
                }
        elif operation == 'write':
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.parent_id,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_notification" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=self.env.user.partner_id.id, uid=self.env.user.id, ids=self.ids))
            for mid, rmod, rid, author_id, parent_id, partner_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'notified': any((message_values[mid].get('notified'), partner_id)),
                    'message_type': message_type,
                }
        elif operation in ('create', 'unlink'):
            self._cr.execute("""SELECT DISTINCT id, model, res_id, author_id, parent_id, message_type FROM "%s" WHERE id = ANY (%%s)""" % self._table, (self.ids,))
            for mid, rmod, rid, author_id, parent_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'message_type': message_type,
                }
        else:
            raise ValueError(_('Wrong operation name (%s)', operation))

        # Author condition (READ, WRITE, CREATE (private))
        author_ids = []
        if operation == 'read':
            author_ids = [mid for mid, message in message_values.items()
                          if (
                                message.get('author_id') and
                                message.get('author_id') == self.env.user.partner_id.id
                            ) or (
                                message.get('create_uid') and
                                message.get('create_uid') == self.env.uid
                            )
                         ]
        elif operation == 'write':
            author_ids = [mid for mid, message in message_values.items() if message.get('author_id') == self.env.user.partner_id.id]
        elif operation == 'create':
            author_ids = [mid for mid, message in message_values.items()
                          if not self.is_thread_message(message)]

        messages_to_check = self.ids
        messages_to_check = set(messages_to_check).difference(set(author_ids))
        if not messages_to_check:
            return

        # Recipients condition, for read and write (partner_ids)
        # keep on top, usefull for systray notifications
        notified_ids = []
        model_record_ids = _generate_model_record_ids(message_values, messages_to_check)
        if operation in ['read', 'write']:
            notified_ids = [mid for mid, message in message_values.items() if message.get('notified')]

        messages_to_check = set(messages_to_check).difference(set(notified_ids))
        if not messages_to_check:
            return

        # CRUD: Access rights related to the document
        document_related_ids = []
        document_related_candidate_ids = [
            mid for mid, message in message_values.items()
            if (message.get('model') and message.get('res_id') and
                message.get('message_type') != 'user_notification')
        ]
        model_record_ids = _generate_model_record_ids(message_values, document_related_candidate_ids)
        for model, doc_ids in model_record_ids.items():
            DocumentModel = self.env[model]
            if hasattr(DocumentModel, '_get_mail_message_access'):
                check_operation = DocumentModel._get_mail_message_access(doc_ids, operation)  ## why not giving model here?
            else:
                check_operation = self.env['mail.thread']._get_mail_message_access(doc_ids, operation, model_name=model)
            records = DocumentModel.browse(doc_ids)
            records.check_access_rights(check_operation)
            mids = records.browse(doc_ids)._filter_access_rules(check_operation)
            document_related_ids += [
                mid for mid, message in message_values.items()
                if (
                    message.get('model') == model and
                    message.get('res_id') in mids.ids and
                    message.get('message_type') != 'user_notification'
                )
            ]

        messages_to_check = messages_to_check.difference(set(document_related_ids))

        if not messages_to_check:
            return

        # Parent condition, for create (check for received notifications for the created message parent)
        notified_ids = []
        if operation == 'create':
            # TDE: probably clean me
            parent_ids = [message.get('parent_id') for message in message_values.values()
                          if message.get('parent_id')]
            self._cr.execute("""SELECT DISTINCT m.id, partner_rel.res_partner_id FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = (%%s)
                WHERE m.id = ANY (%%s)""" % self._table, (self.env.user.partner_id.id, parent_ids,))
            not_parent_ids = [mid[0] for mid in self._cr.fetchall() if mid[1]]
            notified_ids += [mid for mid, message in message_values.items()
                             if message.get('parent_id') in not_parent_ids]

        messages_to_check = messages_to_check.difference(set(notified_ids))
        if not messages_to_check:
            return

        # Recipients condition for create (message_follower_ids)
        if operation == 'create':
            for doc_model, doc_ids in model_record_ids.items():
                followers = self.env['mail.followers'].sudo().search([
                    ('res_model', '=', doc_model),
                    ('res_id', 'in', list(doc_ids)),
                    ('partner_id', '=', self.env.user.partner_id.id),
                    ])
                fol_mids = [follower.res_id for follower in followers]
                notified_ids += [mid for mid, message in message_values.items()
                                 if message.get('model') == doc_model and
                                 message.get('res_id') in fol_mids and
                                 message.get('message_type') != 'user_notification'
                                 ]

        messages_to_check = messages_to_check.difference(set(notified_ids))
        if not messages_to_check:
            return

        if not self.browse(messages_to_check).exists():
            return
        raise AccessError(
            _('The requested operation cannot be completed due to security restrictions. Please contact your system '
              'administrator.\n\n(Document type: %s, Operation: %s)', self._description, operation)
            + ' - ({} {}, {} {})'.format(_('Records:'), list(messages_to_check)[:6], _('User:'), self._uid)
        )
