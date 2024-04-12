# Copyright 2024 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

try:
    from openupgradelib import openupgrade
except Exception:
    from odoo.tools import sql as openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    # Pre-create table/columns
    _logger.info("Pre-creating table stock_picking_resupply")
    if not openupgrade.table_exists(cr, "stock_picking_resupply"):
        cr.execute(
            """
        CREATE TABLE stock_picking_resupply
        (purchase_id INTEGER, picking_id INTEGER);
        """
        )
    _logger.info(
        "Pre-creating column subcontracting_resupply_count for table purchase_order"
    )
    if not openupgrade.column_exists(
        cr, "purchase_order", "subcontracting_resupply_count"
    ):
        cr.execute(
            """
            ALTER TABLE purchase_order
            ADD COLUMN subcontracting_resupply_count INTEGER;
            COMMENT ON COLUMN purchase_order.subcontracting_resupply_count
            IS 'Resupply count';
            """
        )
    _logger.info(
        "Pre-creating column subcontracting_purchase_order_id for table stock_picking"
    )
    if not openupgrade.column_exists(
        cr, "stock_picking", "subcontracting_purchase_order_id"
    ):
        cr.execute(
            """
            ALTER TABLE stock_picking
            ADD COLUMN subcontracting_purchase_order_id INTEGER;
            COMMENT ON COLUMN stock_picking.subcontracting_purchase_order_id
            IS 'Subcontracting order';
            """
        )
    # Fill values
    _logger.info("Pre-computing the table stock_picking_resupply")
    cr.execute(
        """
        INSERT INTO stock_picking_resupply (purchase_id, picking_id)
        SELECT DISTINCT po.id AS purchase_id, sp.id AS picking_id
        FROM purchase_order po
        JOIN purchase_order_line pol ON pol.order_id = po.id
        JOIN stock_move dest ON dest.purchase_line_id = pol.id
        JOIN stock_move_move_rel smmr ON smmr.move_dest_id = dest.id
        JOIN stock_move orig ON smmr.move_orig_id = orig.id
        JOIN mrp_production mp ON orig.production_id = mp.id
        JOIN procurement_group pg ON mp.procurement_group_id = pg.id
        JOIN stock_picking sp ON sp.group_id = pg.id
        WHERE dest.is_subcontract AND dest.state != 'cancel';
        """
    )
    _logger.info(
        "Pre-computing the value of subcontracting_resupply_count for "
        "table purchase_order"
    )
    cr.execute(
        """
        WITH pick_count AS (
            SELECT purchase_id, COUNT(*) AS pick_count
            FROM stock_picking_resupply
            GROUP BY purchase_id
        )
        UPDATE purchase_order po
        SET subcontracting_resupply_count = pc.pick_count
        FROM pick_count pc
        WHERE pc.purchase_id = po.id;
        """
    )
    _logger.info(
        "Pre-computing the value of subcontracting_purchase_order_id for "
        "table stock_picking"
    )
    cr.execute(
        """
        WITH po_sp_rel AS (
            SELECT DISTINCT ON (po.id) po.id AS purchase_id, sp.id AS pick_id
            FROM stock_picking sp
            JOIN stock_move orig ON orig.picking_id = sp.id
            JOIN stock_move_move_rel smmr ON smmr.move_orig_id = orig.id
            JOIN stock_move dest ON smmr.move_dest_id = dest.id
            JOIN mrp_production mp ON dest.raw_material_production_id = mp.id
            JOIN procurement_group pg ON mp.procurement_group_id = pg.id
            JOIN stock_move orig2 ON orig2.group_id = pg.id
            JOIN stock_move_move_rel smmr2 ON smmr2.move_orig_id = orig2.id
            JOIN stock_move dest2 ON smmr2.move_dest_id = dest2.id
            JOIN purchase_order_line pol ON dest2.purchase_line_id = pol.id
            JOIN purchase_order po ON pol.order_id = po.id
            WHERE orig.rule_id IS NOT NULL AND dest2.is_subcontract = TRUE
            GROUP BY sp.id, po.id
            ORDER BY po.id
        )
        UPDATE stock_picking sp
        SET subcontracting_purchase_order_id = po_sp_rel.purchase_id
        FROM po_sp_rel
        WHERE po_sp_rel.pick_id = sp.id;
        """
    )
