# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def rename_column(env, table, old, new):
    cr = env.cr
    if openupgrade.column_exists(cr, table, old):
        openupgrade.rename_columns(cr, {table: [(old, new)]})


@openupgrade.migrate()
def migrate(env, version):
    rename_column(env, "res_users", "schedule_uid", "schedule_user_id")
