# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves_with_no_check = self.filtered(lambda x: x.is_subcontract).with_context(
            skip_negative_qty_check=True
        )
        # For rather unlikely occassions where linked production is not in the right
        # state.
        for move in moves_with_no_check:
            production_move = self.search([("move_dest_ids", "=", move.id)])
            production = production_move.production_id
            if production.reservation_state != "assigned":
                production.action_assign()
            if production.reservation_state == "assigned":
                continue
            moves_with_no_check -= move
        res = super(StockMove, self - moves_with_no_check)._action_done(
            cancel_backorder=cancel_backorder
        )
        res += super(StockMove, moves_with_no_check)._action_done(
            cancel_backorder=cancel_backorder
        )
        return res
