# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    def create_refurbished_stock_move(self):
        self.ensure_one()
        move = self.env["stock.move"].create(self._get_refurbish_stock_move_dict())
        move.quantity_done = self.product_qty
        self.refurbish_move_id = move.id

    def _prepare_repair_stock_move(self):
        res = super()._prepare_repair_stock_move()
        if not self.to_refurbish:
            return res
        else:
            self.create_refurbished_stock_move()
            res.update({"location_dest_id": self.location_dest_id.id})
        return res

    def action_repair_end(self):
        for r in self.filtered(lambda l: l.to_refurbish):
            r.refurbish_move_id._action_done()
        return super().action_repair_end()

    def action_open_stock_moves(self):
        res = super().action_open_stock_moves()
        if self.refurbish_move_id:
            all_move_ids = self.mapped("stock_move_ids").ids + [
                self.refurbish_move_id.id
            ]
            res.update({"domain": [("id", "in", all_move_ids)]})
        return res
