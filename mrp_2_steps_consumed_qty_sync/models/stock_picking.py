# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            picking_type = picking.picking_type_id
            if picking_type == picking_type.warehouse_id.pbm_type_id:
                productions = (
                    picking.move_lines.move_dest_ids.raw_material_production_id
                )
                # Update the component initial demand in production order and assign
                # the moves to cover cases like pick more quantities than expected.
                # In this cases the quantity done is not propagated to linked move
                for move in productions.move_raw_ids:
                    move.product_uom_qty = sum(
                        move.move_orig_ids.filtered(
                            lambda sm: sm.state == "done"
                        ).mapped("quantity_done")
                    )
                productions.move_raw_ids._action_assign()
                productions.move_raw_ids._set_quantities_to_reservation()
        return res
