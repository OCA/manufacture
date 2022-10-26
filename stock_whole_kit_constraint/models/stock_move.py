# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    allow_partial_kit_delivery = fields.Boolean(
        compute="_compute_allow_partial_kit_delivery",
        compute_sudo=True,
    )

    @api.depends("product_id.product_tmpl_id.allow_partial_kit_delivery", "state")
    def _compute_allow_partial_kit_delivery(self):
        """Take it from the product only if it's a kit"""
        self.write({"allow_partial_kit_delivery": True})
        for move in self.filtered(
            lambda x: x.product_id and x.state not in ["done", "cancel"]
        ):
            # If it isn't a kit it will always be True
            if not move.bom_line_id or move.bom_line_id.bom_id.type != "phantom":
                move.allow_partial_kit_delivery = True
                continue
            move.allow_partial_kit_delivery = (
                move.bom_line_id.bom_id.product_tmpl_id.allow_partial_kit_delivery
            )

    def _check_backorder_moves(self):
        """Check if there are partial deliveries on any set of moves. The
        computing is done in the same way the main picking method does it"""
        quantity_todo = {}
        quantity_done = {}
        for move in self:
            quantity_todo.setdefault(move.product_id.id, 0)
            quantity_done.setdefault(move.product_id.id, 0)
            quantity_todo[move.product_id.id] += move.product_uom_qty
            quantity_done[move.product_id.id] += move.quantity_done
        for ops in self.mapped("move_line_ids").filtered(
            lambda x: x.package_id and not x.product_id and not x.move_id
        ):
            for quant in ops.package_id.quant_ids:
                quantity_done.setdefault(quant.product_id.id, 0)
                quantity_done[quant.product_id.id] += quant.qty
        for pack in self.mapped("move_line_ids").filtered(
            lambda x: x.product_id and not x.move_id
        ):
            quantity_done.setdefault(pack.product_id.id, 0)
            quantity_done[pack.product_id.id] += pack.product_uom_id._compute_quantity(
                pack.qty_done, pack.product_id.uom_id
            )
        return any(quantity_done[x] < quantity_todo.get(x, 0) for x in quantity_done)
