# Copyright 2023 Quartile (https://www.quartile.co)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves_with_no_check = self.filtered(lambda x: x.is_subcontract)
        return super(
            StockMove,
            self.with_context(skip_no_negative_move_ids=moves_with_no_check.ids),
        )._action_done(cancel_backorder=cancel_backorder)
