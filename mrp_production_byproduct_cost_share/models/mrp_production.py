# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.constrains("move_byproduct_ids")
    def _check_byproducts(self):
        for order in self:
            if any(move.cost_share < 0 for move in order.move_byproduct_ids):
                raise ValidationError(_("By-products cost shares must be positive."))
            if sum(order.move_byproduct_ids.mapped("cost_share")) > 100:
                raise ValidationError(
                    _(
                        "The total cost share for a manufacturing order's by-products"
                        " cannot exceed 100."
                    )
                )

    def _get_move_finished_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        byproduct_id=False,
    ):
        res = super()._get_move_finished_values(
            product_id, product_uom_qty, product_uom, operation_id, byproduct_id
        )
        res["cost_share"] = (
            0
            if not byproduct_id
            else self.env["mrp.bom.byproduct"].browse(byproduct_id).cost_share
        )
        return res

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves` and
        taking into account cost_share from by-products.
        """
        super(MrpProduction, self)._cal_price(consumed_moves)
        finished_move = self.move_finished_ids.filtered(
            lambda x: x.product_id == self.product_id
            and x.state not in ("done", "cancel")
            and x.quantity_done > 0
        )
        if finished_move:
            finished_move.ensure_one()
            qty_done = finished_move.product_uom._compute_quantity(
                finished_move.quantity_done, finished_move.product_id.uom_id
            )
            # already calculated, but we want to change it according to cost_share
            # from by-products
            total_cost = finished_move.price_unit * qty_done
            byproduct_moves = self.move_byproduct_ids.filtered(
                lambda m: m.state not in ("done", "cancel") and m.quantity_done > 0
            )
            byproduct_cost_share = 0
            for byproduct in byproduct_moves:
                if byproduct.cost_share == 0:
                    continue
                byproduct_cost_share += byproduct.cost_share
                if byproduct.product_id.cost_method in ("fifo", "average"):
                    byproduct.price_unit = (
                        total_cost
                        * byproduct.cost_share
                        / 100
                        / byproduct.product_uom._compute_quantity(
                            byproduct.quantity_done, byproduct.product_id.uom_id
                        )
                    )
            if finished_move.product_id.cost_method in ("fifo", "average"):
                finished_move.price_unit = (
                    total_cost
                    * float_round(
                        1 - byproduct_cost_share / 100, precision_rounding=0.0001
                    )
                    / qty_done
                )
        return True
