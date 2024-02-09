# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _set_quantities_to_reservation(self):
        for move in self:
            if move.is_subcontract:
                move = move.with_context(move_dest_qty=move.product_uom_qty)
                self -= move
                return super(StockMove, move)._set_quantities_to_reservation()
        return super()._set_quantities_to_reservation()
