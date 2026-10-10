# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _is_auto_pick_byproduct(self):
        self.ensure_one()
        production = self.production_id
        return bool(production) and self.product_id != production.product_id

    def _should_auto_pick_byproduct(self):
        self.ensure_one()
        return self.production_id.byproduct_auto_pick

    def write(self, vals):
        # The MO recompute writes byproduct quantities through
        # `_set_quantity_done` under the `auto_conso` context; we must not
        # pick those.
        if self.env.context.get("auto_conso"):
            return super().write(vals)
        candidates = self.filtered(
            lambda move: not move.picked
            and move._is_auto_pick_byproduct()
            and move._should_auto_pick_byproduct()
        )
        quantity_before = {move.id: move.quantity for move in candidates}
        res = super().write(vals)
        candidates.filtered(
            lambda move: float_compare(
                move.quantity,
                quantity_before[move.id],
                precision_rounding=move.product_uom.rounding,
            )
            != 0
        ).picked = True
        return res
