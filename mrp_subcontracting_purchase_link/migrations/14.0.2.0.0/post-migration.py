import logging

_logger = logging.getLogger(__name__)


def update_po_line_in_mrp_production(cr):
    """ """
    _logger.info("Updating PO line in MRP production")
    cr.execute(
        """
        UPDATE mrp_production
        SET
        purchase_line_id = Q.purchase_line_id,
        purchase_order_id = Q.purchase_id
        FROM (
            SELECT po_sm.purchase_line_id, mo_sm.production_id, po.id as purchase_id
            FROM stock_move as po_sm
            INNER JOIN stock_move_move_rel as rel
            ON rel.move_dest_id = po_sm.id
            INNER JOIN stock_move as mo_sm
            ON mo_sm.id = rel.move_orig_id
            INNER JOIN purchase_order_line as pol
            ON pol.id = po_sm.purchase_line_id
            INNER JOIN purchase_order as po
            ON po.id = pol.order_id
            where po_sm.is_subcontract = true
            AND po_sm.purchase_line_id is not null
            AND mo_sm.production_id is not null
            ) AS Q
        WHERE mrp_production.id = Q.production_id
        """
    )


def migrate(cr, version=None):
    if not version:
        return
    update_po_line_in_mrp_production(cr)
