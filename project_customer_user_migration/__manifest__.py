# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Project: Project Customer User — module rename migration',
    'version': '18.0.1.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'One-shot helper that re-points ir.model.data when '
               'customer_project_user is renamed to project_customer_user.',
    'category': 'Hidden',
    'description': '''
Project Customer User — module rename migration
===============================================

    A one-shot, install-then-uninstall helper. It carries the
    ``customer_project_user`` -> ``project_customer_user`` rename by
    re-pointing the module's ``ir.model.data`` rows, so the existing
    ``res.groups`` row (and its ``res_groups_users_rel`` memberships) is kept
    instead of being deleted and re-created.

    Why this is a separate module
    -----------------------------
    The rename cannot be carried by the renamed module itself:

      - a renamed module is ``to install`` under its new name, so its
        ``pre-`` migrations are skipped
        (``odoo/modules/loading.py``: ``if not new_install: migrate_module(..., 'pre')``);
      - its ``post-`` migrations run *after* ``load_data()``, i.e. after
        ``security/groups.xml`` has already created a **second** group under
        the new xmlid;
      - the group's ``ir.model.data`` row has ``noupdate = false``, so
        ``_process_end()`` deletes it — taking the group and its memberships
        with it — because the old xmlid is no longer loaded.

    This module is installed *first*, while the old name is still the
    installed one. Its ``post_init_hook`` re-points the rows before the
    renamed module's XML is ever loaded, so that XML resolves to the existing
    records and updates them in place.

    Ordering
    --------
        1. install project_customer_user_migration    -> re-points ir.model.data
        2. install/upgrade project_customer_user      -> XML updates existing rows
        3. uninstall project_customer_user_migration  -> leaves nothing behind

    It declares no ``depends`` on either module on purpose: it must be
    installable while the old name is the installed one, and it must not drag
    the new module in as a dependency.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-project/project_customer_user',
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'depends': ['base'],
    'data': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': False,
}
