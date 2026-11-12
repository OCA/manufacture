# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import copy

from odoo import models
from odoo.tools import float_compare


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _mto_with_stock_condition(self, move):
        """Extensibility-enhancer method for modifying the scenarios when
        MTO/MTS method should apply."""
        return move.location_id in move.product_id.mrp_mts_mto_location_ids

    def action_assign(self):
        """Reserves available products to the production order but also creates
        procurements for more items if we cannot reserve enough (MTO with
        stock).
        @returns True"""
        # reserve all that is available (standard behaviour):
        res = super().action_assign()
        # try to create procurements:
        move_obj = self.env["stock.move"]
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for production in self:
            warehouse = production.location_src_id.warehouse_id
            mto_with_no_move_dest_id = warehouse.mrp_mto_mts_forecast_qty
            move_ids = copy.copy(production.move_raw_ids.ids)
            for move in move_obj.browse(move_ids):
                new_move = False
                qty_to_procure = 0.0
                if (
                    move.state in ("partially_available", "confirmed")
                    and move.procure_method == "make_to_stock"
                    and mto_with_no_move_dest_id
                    and self._mto_with_stock_condition(move)
                ):
                    qty_to_procure = production.get_mto_qty_to_procure(move)
                    if float_compare(qty_to_procure, 0, precision_digits=precision) > 0:
                        new_move = move
                    else:
                        continue
                if new_move:
                    production.run_procurement(
                        new_move, qty_to_procure, mto_with_no_move_dest_id
                    )
        return res

    def run_procurement(self, move, qty, mto_with_no_move_dest_id):
        self.ensure_one()
        values = move._prepare_procurement_values()
        # In that mode, we don't want any link between the raw material move
        # And the previous move generated now.
        if mto_with_no_move_dest_id:
            values.pop("move_dest_ids", None)
        origin = self.origin or move.origin
        values["route_ids"] = move.product_id.route_ids
        procurement_group = self.env["procurement.group"]
        procurement_group.run(
            [
                procurement_group.Procurement(
                    move.product_id,
                    qty,
                    move.product_uom,
                    move.location_id,
                    origin,
                    origin,
                    move.company_id,
                    values,
                )
            ]
        )
        return True

    def get_mto_qty_to_procure(self, move):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        stock_location_id = move.location_id.id
        move_location = move.with_context(location=stock_location_id)
        virtual_available = move_location.product_id.virtual_available
        qty_available = move.product_id.uom_id._compute_quantity(
            virtual_available, move.product_uom
        )
        if float_compare(qty_available, 0, precision_digits=precision) >= 0:
            return 0.0
        else:
            if (
                float_compare(
                    abs(qty_available), move.product_uom_qty, precision_digits=precision
                )
                < 0
            ):
                return abs(qty_available)
        return move.product_uom_qty
