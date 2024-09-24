#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_is_zero


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def _remove_empty_move_values(self, moves_values):
        """Remove values that have no quantity."""
        clean_moves_raw_values = []
        for move_values in moves_values:
            product = self.env["product.product"].browse(move_values["product_id"])
            quantity = move_values["product_uom_qty"]
            if not float_is_zero(quantity, precision_rounding=product.uom_id.rounding):
                clean_moves_raw_values.append(move_values)
        return clean_moves_raw_values

    def _get_moves_raw_values(self):
        moves_raw_values = super()._get_moves_raw_values()
        return self._remove_empty_move_values(moves_raw_values)
