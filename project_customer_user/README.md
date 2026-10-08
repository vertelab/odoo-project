# Project Customer User

A user type for project customers: a partner who is shared on a project gets
backend access to that project and its tasks — and nothing else.

## What it does

- Defines the **Project Customer** group (`group_project_customer_user`).
- Grants the group the ACLs of the project source groups by **mirroring** them
  (`models/ir_model_access.py`) instead of implying `project.group_project_user`
  — implying it would re-import the full internal surface via `base.group_user`.
- Denies every model not on an explicit whitelist via a **deny layer**
  (`models/ir_rule.py`), because `ir.rule` domains are ANDed and can therefore
  subtract from a group the user also holds, while `ir.model.access` rows are
  ORed and cannot.
- Scopes record access to `partner_id` ∨ `customer_ids` on the project
  (`security/groups.xml`).
- Keeps customers out of internal mail threads (`models/mail_guard.py`) while
  letting them be full participants in the chatter on their own projects.

## Granting a Project Customer (two steps, both required)

1. **Settings → Users → Access Rights → Project → "Project Customer"**
   The group supplies the rights.
2. **Project → Settings → the "Customers" field (`customer_ids`) → add the
   contact**
   The field supplies the access.

The group alone is not enough, and the field alone is not enough.

## Module name

Renamed from `customer_project_user` to `project_customer_user` in
`18.0.1.0.0`, to match the `project_*` naming of the rest of this repository.

Because Odoo does not move a module's `ir.model.data` rows when a module is
renamed, an installed database needs the companion module
**`project_customer_user_migration`** applied first:

```
1. checkmodule -m project_customer_user_migration    # re-points ir.model.data
2. checkmodule -m project_customer_user              # XML updates the existing rows
3. checkmodule -m project_customer_user_migration --uninstall
```

Skipping step 1 makes Odoo create a **second** "Project Customer" group and
orphan the existing one — including its user memberships. See that module's
`hooks.py` for the full explanation and the rollback procedure.

## Layout

```
security/groups.xml          group, hand-written ACLs, record rules
models/ir_model_access.py    ACL mirror (SOURCE_GROUPS -> customer group)
models/ir_rule.py            deny layer (ALLOWED_MODELS whitelist)
models/res_users_groups.py   group allow-list (ALLOWED_GROUPS)
models/mail_guard.py         notification recipient filter
models/project.py            customer_ids field, _search() defence in depth
controllers/web.py           login redirect
migrations/                  historical upgrade scripts (pre-rename)
```

## Adding a Project-adjacent module

Append its group to `SOURCE_GROUPS` in `models/ir_model_access.py`, and any new
model the customer must reach to `ALLOWED_MODELS` in `models/ir_rule.py`. The
syncs run on install, on upgrade, and on every registry load, so no version
bump is needed for the whitelist to take effect.
