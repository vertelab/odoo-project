import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

CUSTOMER_GROUP = 'customer_project_user.group_project_customer_user'

# Landing action for Project Customer users.
#
# `res.users.action_id` is the documented Odoo mechanism for this:
#   "If specified, this action will be opened at log on for this user, in
#    addition to the standard menu."
#
# Using it means we do NOT have to touch the portal redirect. The customer
# still reaches /my (they are share=True, so portal/controllers/web.py sends
# them there), but the action is what opens on logon — and because the action
# is project.project, that is where they land.
#
# `project.open_view_project_all` is res_model=project.project,
# view_mode=kanban,list,form (verified on ledningssystem 2026-10-03).
LANDING_ACTION = 'project.open_view_project_all'


class ResUsers(models.Model):
    _inherit = 'res.users'

    # NOTE: there is deliberately NO _is_internal() override here.
    #
    # This module used to force _is_internal() to True for Project Customer
    # users while also implying base.group_user. Both were removed together
    # (design D2) because they are two halves of the same problem:
    #
    #   implied base.group_user  -> the customer *is* an internal user, with
    #                               460 inherited ACL rows (ledningssystem,
    #                               2026-10-03)
    #   _is_internal() -> True   -> core code that branches on internal-ness
    #                               (30 call sites, 18 in `mail`) treats the
    #                               customer as staff
    #
    # Leaving the override in place after removing the group would produce an
    # inconsistent state: non-internal by ACL, internal by flag. `mail` and
    # `web` would assume access the ACLs deny, and failures would become
    # data-dependent rather than systematic.
    #
    # The customer is a non-internal backend user with an explicit, mirrored
    # ACL set (design D1).

    # ------------------------------------------------------------------
    # Landing action
    # ------------------------------------------------------------------

    @api.model
    def _customer_landing_action_id(self):
        """Return the landing action id, or False if unavailable."""
        action = self.env.ref(LANDING_ACTION, raise_if_not_found=False)
        return action.id if action else False

    def _customer_apply_landing_action(self):
        """Set action_id on every Project Customer that has none.

        Only fills a blank action_id: an explicit choice made by an
        administrator is never overwritten. Idempotent.
        """
        group = self.env.ref(CUSTOMER_GROUP, raise_if_not_found=False)
        action_id = self._customer_landing_action_id()
        if not group or not action_id:
            return 0
        customers = self.sudo().search(
            [('groups_id', 'in', group.id), ('action_id', '=', False)]
        )
        if customers:
            customers.sudo().write({'action_id': action_id})
        return len(customers)

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users._customer_apply_landing_action()
        return users

    def write(self, vals):
        result = super().write(vals)
        # A user added to the customer group after creation must also get the
        # landing action. Checking groups_id covers both the plain group write
        # and the customer-group cleanup, which writes groups_id too.
        if 'groups_id' in vals:
            self._customer_apply_landing_action()
            self._customer_sync_deny_layer()
        return result

    @api.model
    def _customer_sync_deny_layer(self):
        """Re-sync the deny layer after a group change.

        The deny set is derived from what customer users can reach, so it
        changes when a customer's groups change. Without this, a user granted
        the customer group keeps whatever the other groups gave them until the
        next module upgrade — which is how hr.employee leaked 46 rows on
        2026-10-03.
        """
        try:
            self.env['ir.rule']._deny_sync_customer_rules()
        except Exception:  # never break a user write
            _logger.exception(
                "customer_project_user: deny layer sync failed after a "
                "groups_id write"
            )
