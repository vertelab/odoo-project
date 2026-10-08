# Repo-definition update for the `project_customer_user` rename

`docs/repo-rename-project_customer_user.patch` contains the change needed in
`/home/waland/salt/odoo/repos/` when `customer_project_user` is renamed to
`project_customer_user`.

## What it does

One line per file, in the `modules:` list:

```
-customer_project_user,
+project_customer_user,project_customer_user_migration,
```

The migration module is added to the list because it must be installed **before**
the renamed module — see `project_customer_user_migration/README.md`.

## Files

- `master.repo`
- `ledningssystem.repo`
- `laginyadviceab.repo`

## Applying

The files live in another user's working tree (`waland:waland`) and are tracked
in `git.vertel.se:vertelab/salt.git`, so the patch is kept here rather than
applied from this repository:

```bash
cd /home/waland/salt/odoo/repos
patch -p0 < /usr/share/odoo-project/docs/repo-rename-project_customer_user.patch
```

The patch was generated against the file contents of 2026-10-08. If the
`modules:` lines have changed since, re-apply by hand:

```bash
sed -i 's/\bcustomer_project_user,/project_customer_user,project_customer_user_migration,/' \
    master.repo ledningssystem.repo laginyadviceab.repo
```

## Verification

```bash
grep -rn "customer_project_user" /home/waland/salt/odoo/repos/   # must be empty
grep -c "project_customer_user_migration" /home/waland/salt/odoo/repos/*.repo
```
