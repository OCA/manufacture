# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    fixed_consumption = fields.Boolean(related="bom_id.fixed_consumption")

    def _set_qty_producing(self, pick_manual_consumption_moves=True):
        res = super()._set_qty_producing(
            pick_manual_consumption_moves=pick_manual_consumption_moves
        )
        if not self.fixed_consumption or not self.qty_producing:
            return res
        for move in self.move_raw_ids:
            # Keep what the user registered by hand, as the standard flow does.
            if move.picked and move.manual_consumption:
                continue
            if move.sudo()._should_bypass_set_qty_producing():
                continue
            move._set_quantity_done(move._get_fixed_consumption_qty())
            if (
                (not move.manual_consumption or pick_manual_consumption_moves)
                and move.quantity
                and move.raw_material_production_id
            ):
                move.picked = True
        return res

    def _get_consumption_issues(self):
        fixed = self.filtered("fixed_consumption")
        issues = super(MrpProduction, self - fixed)._get_consumption_issues()
        if self.env.context.get("skip_consumption"):
            return issues
        # Same check as the standard one, but the expected quantity is the
        # planned one instead of the one scaled by the produced quantity.
        for order in fixed:
            if (
                order.consumption == "flexible"
                or not order.bom_id
                or not order.bom_id.bom_line_ids
            ):
                continue
            expected_qty_by_product = defaultdict(float)
            for move_values in order._get_moves_raw_values():
                product = self.env["product.product"].browse(move_values["product_id"])
                uom = self.env["uom.uom"].browse(move_values["product_uom"])
                expected_qty_by_product[product] += uom._compute_quantity(
                    move_values["product_uom_qty"], product.uom_id
                )
            done_qty_by_product = defaultdict(float)
            for move in order.move_raw_ids:
                quantity = move.product_uom._compute_quantity(
                    move._get_picked_quantity(), move.product_id.uom_id
                )
                if (
                    move.product_id not in expected_qty_by_product
                    and move.picked
                    and not move.product_id.uom_id.is_zero(quantity)
                ):
                    issues.append((order, move.product_id, quantity, 0.0))
                    continue
                done_qty_by_product[move.product_id] += quantity if move.picked else 0.0
            for product, qty_to_consume in expected_qty_by_product.items():
                quantity = done_qty_by_product.get(product, 0.0)
                if product.uom_id.compare(qty_to_consume, quantity) != 0:
                    issues.append((order, product, quantity, qty_to_consume))
        return issues
