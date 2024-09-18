# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        # It is necessary to apply the key context to skip the error in the
        # subcontracting process
        if self.env.context.get("subcontract_move_id"):
            self = self.with_context(skip_negative_qty_check=True)
        moves_with_no_check = self.filtered(lambda x: x.is_subcontract).with_context(
            skip_negative_qty_check=True
        )
        # For rather unlikely occassions where linked production is not in the right
        # state.
        for move in moves_with_no_check:
            production_moves = self.search(
                [
                    ("move_dest_ids", "=", move.id),
                    ("state", "not in", ("done", "cancel")),
                ]
            )
            productions = production_moves.production_id
            unassigned_productions = productions.filtered(
                lambda p: p.reservation_state != "assigned"
            )
            unassigned_productions.action_assign()
            if all(
                state == "assigned"
                for state in unassigned_productions.mapped("reservation_state")
            ):
                continue
            moves_with_no_check -= move
        res = super(StockMove, self - moves_with_no_check)._action_done(
            cancel_backorder=cancel_backorder
        )
        res += super(StockMove, moves_with_no_check)._action_done(
            cancel_backorder=cancel_backorder
        )
        return res
