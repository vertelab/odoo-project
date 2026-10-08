# Copyright 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Carry the ``customer_project_user`` -> ``project_customer_user`` rename.

What this does
--------------
One ``UPDATE`` on ``ir.model.data``:

    module = 'customer_project_user'  ->  module = 'project_customer_user'

That is the whole migration. Everything else follows from it:

  - ``env.ref('project_customer_user.group_project_customer_user')`` starts
    resolving to the *existing* ``res.groups`` row (id 88 on ledningssystem),
  - so when the renamed module's ``security/groups.xml`` is loaded, Odoo updates
    that row in place instead of creating a second group,
  - and because the group row is never touched, ``res_groups_users_rel`` (the
    memberships) is preserved untouched.

Why it must run before the renamed module loads
-----------------------------------------------
Verified against the framework on 2026-10-08 (isolated test database):

  1. A renamed module is ``to install`` under its new name, so its ``pre-``
     migrations are skipped:

         odoo/modules/loading.py
         if needs_update:
             if not new_install:
                 migrations.migrate_module(package, 'pre')   # <- not reached

  2. Its ``post-`` migrations run *after* the XML:

         load_data(env, idref, mode, kind='data', package=package)
         migrations.migrate_module(package, 'post')          # <- too late

     By then ``security/groups.xml`` has already created a second group.

  3. The group's ``ir.model.data`` row has ``noupdate = false``, so
     ``IrModelData._process_end()`` deletes it — the old xmlid is no longer in
     ``pool.loaded_xmlids`` — and deleting the xmlid row takes the group and its
     memberships with it.

  4. Counter-check: a row whose ``module`` is *not* loaded in the run survives
     ``_process_end`` untouched, and ``write({"module": ...})`` on
     ``ir.model.data`` does work through the ORM. Hence re-pointing works, and
     hence this module can safely do it while the old name is still installed.

Idempotency
-----------
The hook is a single ``UPDATE ... WHERE module = 'customer_project_user'``.
Re-running it is a no-op (0 rows). Running it on a database that never had the
old name is also a no-op. It never creates, deletes or renames the group row
itself, and it never touches ``ir_module_module``.

Rollback
--------
Reverse the direction and run it again:

    UPDATE ir.model.data
       SET module = 'customer_project_user'
     WHERE module = 'project_customer_user'
       AND name IN (<the xmlids this module owns>)

Then restore the old directory name and ``-u customer_project_user``. Because
only the ``module`` column moves, no membership is lost in either direction.

To reverse on a live database, set the direction explicitly instead of editing
this file — the hook reads ``OLD_MODULE``/``NEW_MODULE`` from the module's
``ir.config_parameter`` if present:

    project_customer_user_migration.source_module
    project_customer_user_migration.target_module

That keeps the reversal a configuration change rather than a code change, so
the same module version can be used in both directions.
"""

import logging

_logger = logging.getLogger(__name__)

OLD_MODULE = "customer_project_user"
NEW_MODULE = "project_customer_user"

PARAM_SOURCE = "project_customer_user_migration.source_module"
PARAM_TARGET = "project_customer_user_migration.target_module"


def _resolve_direction(env):
    """Return (source, target) module names.

    Defaults to the forward rename. An operator can reverse it by setting the
    two ``ir.config_parameter`` keys above, so the same module version carries
    the rollback without a code change.
    """
    params = env["ir.config_parameter"].sudo()
    source = params.get_param(PARAM_SOURCE, OLD_MODULE)
    target = params.get_param(PARAM_TARGET, NEW_MODULE)
    return source, target


def post_init_hook(env):
    """Re-point the module's ``ir.model.data`` rows to the new module name."""
    source, target = _resolve_direction(env)

    if source == target:
        _logger.warning(
            "project_customer_user_migration: source and target are both %r; "
            "nothing to do",
            source,
        )
        return

    cr = env.cr

    # Count first so the log is meaningful and the no-op case is explicit.
    cr.execute(
        "SELECT count(*) FROM ir_model_data WHERE module = %s", (source,)
    )
    before = cr.fetchone()[0]

    if not before:
        _logger.info(
            "project_customer_user_migration: no ir.model.data rows for %r; "
            "nothing to do (already migrated, or the module was never "
            "installed under that name)",
            source,
        )
        return

    cr.execute(
        "UPDATE ir_model_data SET module = %s WHERE module = %s",
        (target, source),
    )
    updated = cr.rowcount

    # The xmlid lookup is ORM-cached; drop the cache so the new names resolve
    # in this same transaction.
    env.registry.clear_cache()

    _logger.info(
        "project_customer_user_migration: re-pointed %s ir.model.data row(s) "
        "from %r to %r (found %s before the update)",
        updated,
        source,
        target,
        before,
    )

    # Sanity check: the group must still resolve, under the new name.
    group = env.ref(
        "%s.group_project_customer_user" % target, raise_if_not_found=False
    )
    if group:
        cr.execute(
            "SELECT count(*) FROM res_groups_users_rel WHERE gid = %s",
            (group.id,),
        )
        members = cr.fetchone()[0]
        _logger.info(
            "project_customer_user_migration: group %r resolves to id=%s with "
            "%s member(s) — memberships preserved",
            "%s.group_project_customer_user" % target,
            group.id,
            members,
        )
    else:
        _logger.warning(
            "project_customer_user_migration: %r does not resolve after the "
            "update. If the customer module was never installed under %r this "
            "is expected; otherwise the rename needs attention.",
            "%s.group_project_customer_user" % target,
            source,
        )
