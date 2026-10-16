# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        if not self.env["stock.move"]._is_consumed_qty_sync_enabled():
            return res
        for picking in self:
            picking_type = picking.picking_type_id
            if picking_type == picking_type.warehouse_id.pbm_type_id:
                productions = (
                    picking.move_lines.move_dest_ids.raw_material_production_id
                )
                # Update the component initial demand in production order and assign
                # the moves to cover cases like pick more quantities than expected.
                # In this cases the quantity done is not propagated to linked move.
                # Pending origin moves (e.g. backorders) must keep their demand in
                # the production order, so count them by their initial demand.
                for move in productions.move_raw_ids.filtered(
                    lambda sm: sm.state not in ("done", "cancel") and sm.move_orig_ids
                ):
                    move.product_uom_qty = move._get_pick_demand()
                productions.move_raw_ids._action_assign()
                # Quantities consumed before picking (e.g. when a work order is
                # started) must not remain on components still pending in the
                # pick, as they have not been picked yet.
                unpicked_moves = productions.move_raw_ids.filtered(
                    lambda sm: sm.state not in ("done", "cancel")
                    and any(
                        orig.picking_type_id == picking_type
                        and orig.state not in ("done", "cancel")
                        for orig in sm.move_orig_ids
                    )
                )
                unpicked_moves.move_line_ids.filtered(
                    lambda ml: ml.state not in ("done", "cancel")
                    and float_is_zero(
                        ml.product_uom_qty,
                        precision_rounding=ml.product_uom_id.rounding,
                    )
                ).unlink()
                productions.move_raw_ids._set_quantities_to_reservation()
        return res
