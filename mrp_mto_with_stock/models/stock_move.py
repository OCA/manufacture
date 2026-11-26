# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self, picking_type_code=False):
        """When configured as MTO/MTS manufacturing location, if there is
        stock available unreserved, use it and procure the remaining."""
        res = super()._adjust_procure_method(picking_type_code=picking_type_code)
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            production = move.raw_material_production_id
            if not production or not production._mto_with_stock_condition(move):
                continue
            if production.location_src_id.warehouse_id.mrp_mto_mts_forecast_qty:
                continue
            # We have to split the move because we can't have
            # a part of the move that have ancestors and not the
            # other else it won't ever be reserved.
            qty_to_procure = min(
                move.product_uom_qty - move.product_id.free_qty,
                move.product_uom_qty,
            )
            if (
                qty_to_procure > 0.0
                and float_compare(
                    qty_to_procure, move.product_uom_qty, precision_digits=precision
                )
                < 0
            ):
                # we need to adjust the unit_factor of the stock moves
                # to split correctly the load of each one.
                ratio = qty_to_procure / move.product_uom_qty
                # create new move for make to order part
                mto_move = move.copy(
                    {
                        "product_uom_qty": qty_to_procure,
                        "procure_method": "make_to_order",
                        "unit_factor": move.unit_factor * ratio,
                    }
                )
                move.write(
                    {
                        "product_uom_qty": move.product_uom_qty - qty_to_procure,
                        "unit_factor": move.unit_factor * (1 - ratio),
                    }
                )
                # The new move is not part of the set of moves that the
                # production is going to confirm, so confirm it here.
                mto_move._action_confirm(merge=False)
        return res
