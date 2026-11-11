# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _push_mto_qty_filter_moves(self, visited_ids):
        """Return the moves of `self` whose demand can be adjusted.

        Done and cancelled moves cannot be changed, and components moves of
        another manufacturing order are left untouched.
        """
        return self.filtered(
            lambda m: m.state not in ("done", "cancel")
            and not m.raw_material_production_id
            and m.id not in visited_ids
        )

    def _push_mto_qty(self, qty, uom):
        """Change the demand of `self` (and of their own destination moves)
        by `qty` expressed in `uom`.

        A positive `qty` increases the demand of the earliest move, a negative
        `qty` decreases the demand of the latest moves first. Moves whose demand
        is reduced to zero are cancelled.
        """
        if uom.is_zero(qty):
            return
        adjusted, to_cancel = self._push_mto_qty_apply(qty, uom, set())
        if to_cancel:
            to_cancel._action_cancel()
        to_assign = (adjusted - to_cancel).filtered(
            lambda m: m.state in ("confirmed", "waiting", "partially_available")
        )
        if to_assign:
            to_assign._action_assign()

    def _push_mto_qty_apply(self, qty, uom, visited_ids):
        adjusted = to_cancel = self.env["stock.move"]
        moves = self._push_mto_qty_filter_moves(visited_ids)
        if not moves or uom.is_zero(qty):
            return adjusted, to_cancel
        visited_ids.update(moves.ids)
        if qty > 0:
            moves = moves.sorted(lambda m: (m.date, m.id))[:1]
        else:
            moves = moves.sorted(lambda m: (m.date, m.id), reverse=True)
        remaining = qty
        for move in moves:
            if uom.compare(remaining, 0) == 0:
                break
            if remaining > 0:
                applied = remaining
            else:
                move_qty = move.product_uom._compute_quantity(
                    move.product_uom_qty, uom, round=False
                )
                applied = max(remaining, -move_qty)
            remaining -= applied
            new_qty = move.product_uom_qty + uom._compute_quantity(
                applied, move.product_uom
            )
            if move.product_uom.compare(new_qty, 0) <= 0:
                new_qty = 0.0
                to_cancel |= move
            # no_procurement prevents mrp from running a new procurement
            # for the updated demand
            move.with_context(no_procurement=True).product_uom_qty = new_qty
            adjusted |= move
            sub_adjusted, sub_to_cancel = move.move_dest_ids._push_mto_qty_apply(
                applied, uom, visited_ids
            )
            adjusted |= sub_adjusted
            to_cancel |= sub_to_cancel
        return adjusted, to_cancel
