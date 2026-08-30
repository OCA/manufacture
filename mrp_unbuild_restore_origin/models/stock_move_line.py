# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _apply_putaway_strategy(self):
        # Avoid changing locations if exact_location context is set
        if not self.env.context.get("exact_location"):
            return super()._apply_putaway_strategy()
        original_locations = {ml: (ml.location_id, ml.location_dest_id) for ml in self}
        res = super()._apply_putaway_strategy()
        for ml in self:
            ml.location_id, ml.location_dest_id = original_locations[ml]
        return res
