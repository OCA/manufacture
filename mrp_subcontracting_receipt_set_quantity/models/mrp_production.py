# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _has_tracked_component(self):
        # If production is already done for the subcontracting recept move, return False
        # to indicate that the move should not be excluded from the set quantity
        # process.
        move_dest_qty = self._context.get("move_dest_qty")
        if move_dest_qty and move_dest_qty == self.qty_produced:
            return False
        return super()._has_tracked_component()
