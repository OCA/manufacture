# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_fixed_consumption_qty(self):
        """Quantity to consume when the order has a fixed consumption: the
        planned demand, capped for tracked components by the quantity
        delivered by the previous moves, as the standard flow does."""
        self.ensure_one()
        new_qty = self.product_uom_qty
        if self.has_tracking == "none":
            return new_qty
        relevant_orig = self.move_orig_ids.filtered(
            lambda m: m.state not in ("draft", "cancel")
        )
        if not relevant_orig:
            return new_qty
        qty_available = sum(
            orig.product_uom._compute_quantity(orig.quantity, self.product_uom)
            for orig in relevant_orig.filtered(lambda m: m.state == "done")
        )
        qty_taken = sum(
            sibling.product_uom._compute_quantity(sibling.quantity, self.product_uom)
            for sibling in (self.move_orig_ids.move_dest_ids - self).filtered(
                lambda m: m.state == "done"
            )
        )
        if self.product_uom.compare(qty_available, qty_taken) >= 0:
            new_qty = min(new_qty, qty_available - qty_taken)
        return new_qty
