# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_helper_target_field_qty(self):
        production_moves = self.filtered(
            lambda m: m.raw_material_production_id or m.production_id
        )
        return super(
            StockMove,
            self - production_moves + production_moves._keep_qty_matching_secondary(),
        )._compute_helper_target_field_qty()
