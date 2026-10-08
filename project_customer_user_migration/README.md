# Project Customer User — module rename migration

A one-shot, install-then-uninstall helper. It carries the
`customer_project_user` → `project_customer_user` rename by re-pointing the
module's `ir.model.data` rows, so the existing `res.groups` row (and its
`res_groups_users_rel` memberships) is kept instead of being deleted and
re-created.

## Usage

```
1. checkmodule -m project_customer_user_migration    # re-points ir.model.data
2. checkmodule -m project_customer_user              # XML updates the existing rows
3. checkmodule -m project_customer_user_migration --uninstall
```

Step 3 is safe: this module owns no records of its own.

## Why this is a separate module

The rename cannot be carried by the renamed module itself. Verified against
Odoo 18 on 2026-10-08:

1. **`pre-` migrations do not run.** A renamed module is `to install` under its
   new name, so `odoo/modules/loading.py` skips the `pre-` stage:

   ```python
   if needs_update:
       if not new_install:
           migrations.migrate_module(package, 'pre')
   ```

2. **`post-` migrations run too late.** `load_data()` (the XML) runs *before*
   `migrate_module(package, 'post')`, so by then `security/groups.xml` has
   already created a second group.

3. **The group's `ir.model.data` row has `noupdate = false`**, so
   `IrModelData._process_end()` deletes it — the old xmlid is no longer loaded —
   and deleting the xmlid row takes the group and its memberships with it.

Installing this module *first* re-points the rows while the old name is still
the installed one, so the renamed module's XML resolves to the existing records
and updates them in place.

## Rollback

Reverse the direction and run it again. Set the two parameters, then install
the module:

```
project_customer_user_migration.source_module = project_customer_user
project_customer_user_migration.target_module = customer_project_user
```

Then restore the old directory name and `-u customer_project_user`. Because
only the `module` column moves, no membership is lost in either direction.

## Idempotency

The hook is a single `UPDATE ... WHERE module = <source>`. Re-running it is a
no-op (0 rows), and running it on a database that never had the old name is also
a no-op. It never creates, deletes or renames the group row itself.
