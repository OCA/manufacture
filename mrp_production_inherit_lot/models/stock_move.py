# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, *args, **kwargs):
        vals = super()._prepare_move_line_vals(*args, **kwargs)
        if (
            self.production_id
            and self.byproduct_id
            and self.byproduct_id.inherit_lot
            and self.production_id.lot_producing_ids
        ):
            vals["lot_id"] = self.production_id._generate_byproduct_lot(
                self.byproduct_id
            ).id
        return vals
