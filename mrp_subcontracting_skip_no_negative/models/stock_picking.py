# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        self._check_negative_quants_after_process()
        return res

    def _check_negative_quants_after_process(self):
        product_ids = self.mapped("move_ids.product_id.id")
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "in", product_ids),
            ]
        )
        quants.check_negative_qty()

    def _get_moves_to_backorder(self):
        self.ensure_one()
        moves = super()._get_moves_to_backorder()
        if self.env.context.get("skip_negative_qty_check"):
            return moves.filtered(lambda x: x.is_subcontract)
        return moves

    def _create_backorder_picking(self):
        self.ensure_one()
        existing_backorder_picking = self.env["stock.picking"].search(
            [("backorder_id", "=", self.id)]
        )
        existing_subcontract_moves = existing_backorder_picking.move_ids.filtered(
            lambda x: x.is_subcontract
        )
        if (
            self.move_ids.filtered(lambda x: x.state == "done" and x.is_subcontract)
            and existing_subcontract_moves
        ):
            return existing_backorder_picking
        return super()._create_backorder_picking()
