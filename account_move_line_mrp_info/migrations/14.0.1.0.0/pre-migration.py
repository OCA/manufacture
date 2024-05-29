# Copyright 2024 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "account.move.line",
                "account_move_line",
                "manufacture_order_id",
                "mrp_production_id",
            ),
            (
                "account.move.line",
                "account_move_line",
                "unbuild_order_id",
                "unbuild_id",
            ),
        ],
    )
