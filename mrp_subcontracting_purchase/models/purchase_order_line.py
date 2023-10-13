from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _compute_qty_received(self):
        """Returns the quantity comes for moves"""
        pol_obj = self.env["purchase.order.line"]
        for line in self.filtered(
            lambda l: l.qty_received_method == "stock_moves"
            and l.move_ids.filtered(lambda m: m.state != "cancel")
        ):
            kit_bom = self.env["mrp.bom"]._bom_find(
                product=line.product_id,
                company_id=line.company_id.id,
                bom_type="phantom",
            )
            if kit_bom:
                pol_obj |= self._set_qty_received(kit_bom, line)
        super(PurchaseOrderLine, self - pol_obj)._compute_qty_received()

    @api.model
    def _set_qty_received(self, kit_bom, line):
        """Set qty received on the basis of the bom"""
        moves = line.move_ids.filtered(lambda m: m.state == "done" and not m.scrapped)
        order_qty = line.product_uom._compute_quantity(
            line.product_uom_qty, kit_bom.product_uom_id
        )
        filters = {
            "incoming_moves": lambda m: m.location_id.usage == "supplier"
            and (
                not m.origin_returned_move_id
                or (m.origin_returned_move_id and m.to_refund)
            ),
            "outgoing_moves": lambda m: m.location_id.usage != "supplier"
            and m.to_refund,
        }
        line.qty_received = moves._compute_kit_quantities(
            line.product_id, order_qty, kit_bom, filters
        )
        return line
