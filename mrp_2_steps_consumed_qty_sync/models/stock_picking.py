# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        if not self.env["stock.move"]._is_consumed_qty_sync_enabled():
            return res
        for picking in self:
            picking_type = picking.picking_type_id
            if picking_type == picking_type.warehouse_id.pbm_type_id:
                productions = picking.move_ids.move_dest_ids.raw_material_production_id
                # Update the component initial demand in production order and assign
                # the moves to cover cases like pick more quantities than expected.
                # In this cases the quantity done is not propagated to linked move.
                # Pending origin moves (e.g. backorders) must keep their demand in
                # the production order, so count them by their initial demand.
                # The consumption is what has been picked: the reservation is
                # rebuilt from the done picks, which drops quantities set before
                # picking (e.g. when a work order is started). Components already
                # marked as consumed keep the mark with the picked quantities.
                pick_moves = productions.move_raw_ids.filtered(
                    lambda sm: sm.state not in ("done", "cancel")
                    and sm._is_consumed_from_pick()
                )
                picked_moves = pick_moves.filtered("picked")
                pick_moves.picked = False
                pick_moves._do_unreserve()
                for move in productions.move_raw_ids.filtered(
                    lambda sm: sm.state not in ("done", "cancel") and sm.move_orig_ids
                ):
                    move.product_uom_qty = move._get_pick_demand()
                productions.move_raw_ids._action_assign()
                picked_moves.filtered("quantity").picked = True
        return res
