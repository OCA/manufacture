# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tools.sql import column_exists, create_column


def fill_stock_lot_bom_id(cr):
    cr.execute(
        """
        UPDATE stock_lot sl
        SET bom_id = mp.bom_id
        FROM (
            SELECT DISTINCT ON (lot_producing_id) lot_producing_id, bom_id
            FROM mrp_production
            WHERE state = 'done' AND lot_producing_id IS NOT NULL
            ORDER BY
                lot_producing_id,
                COALESCE(date_finished, create_date) DESC,
                id DESC
        ) mp
        WHERE sl.id = mp.lot_producing_id AND mp.bom_id IS NOT NULL
        """
    )


def fill_stock_quant_bom_id(cr):
    cr.execute(
        """
        UPDATE stock_quant sq
        SET bom_id = sl.bom_id
        FROM stock_lot sl
        WHERE sq.lot_id = sl.id AND sl.bom_id IS NOT NULL
        """
    )


def pre_init_hook(env):
    if not column_exists(env.cr, "stock_lot", "bom_id"):
        create_column(env.cr, "stock_lot", "bom_id", "int4")
        fill_stock_lot_bom_id(env.cr)
    if not column_exists(env.cr, "stock_quant", "bom_id"):
        create_column(env.cr, "stock_quant", "bom_id", "int4")
        fill_stock_quant_bom_id(env.cr)
