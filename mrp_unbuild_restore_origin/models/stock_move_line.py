# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _apply_putaway_strategy(self):
        # Avoid changing locations if exact_location context is set
        location_id = False
        location_dest_id = False
        if self.env.context.get("exact_location"):
            location_id = self.location_id.id
            location_dest_id = self.location_dest_id.id
        super()._apply_putaway_strategy()
        if location_id and location_dest_id:
            self.location_id = location_id
            self.location_dest_id = location_dest_id
        return
