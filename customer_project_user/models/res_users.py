from odoo import models


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
