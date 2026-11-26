# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        if (
            "quantity" not in vals
            or "qty_picked" in vals
            or not self.env.context.get("mrp_set_qty_producing")
        ):
            return super().write(vals)
        following = self.filtered(lambda ml: ml._qty_picked_follows_quantity())
        res = super().write(vals)
        for line in following:
            if float_compare(
                line.qty_picked,
                line.quantity,
                precision_rounding=line.product_uom_id.rounding,
            ):
                line._pick_qty(line.quantity)
        return res

    def _qty_picked_follows_quantity(self):
        self.ensure_one()
        move = self.move_id
        return (
            self.picked
            and bool(move.raw_material_production_id or move.production_id)
            and not float_compare(
                self.qty_picked,
                self.quantity,
                precision_rounding=self.product_uom_id.rounding,
            )
        )
