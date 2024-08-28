# Copyright (C) 2022 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class Repair(models.Model):
    _inherit = "repair.order"

    remaining_quantity = fields.Float(
        "Remaining quantity to be transferred", compute="_compute_remaining_quantity"
    )

    def _compute_remaining_quantity(self):
        for rec in self:
            remaining_quantity = rec.product_qty
            if rec.picking_ids:
                stock_moves = rec.picking_ids.mapped("move_lines").filtered(
                    lambda x: x.state != "cancel"
                )
                remaining_quantity = rec.product_qty - sum(
                    stock_moves.mapped("product_uom_qty")
                )
            rec.remaining_quantity = remaining_quantity

    def action_transfer_done_moves(self):
        self.ensure_one()
        return {
            "name": "Transfer repair moves",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "repair.move.transfer",
            "context": {
                "default_repair_order_id": self.id,
                "default_quantity": self.remaining_quantity,
            },
            "target": "new",
        }
