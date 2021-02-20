# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _prepare_tracking_item_values(self):
        vals = super()._prepare_tracking_item_values()
        vals.update(
            {
                "stock_move_id": self.stock_move_id.id,
                "workorder_id": self.workorder_id.id,
            }
        )
        return vals

    def _get_tracking_item(self):
        """
        Locate existing Tracking Item.
        - For Work Order, locate by Work Order
        - For Stock Moves, locate by Product.

        NOTE: multiple Stock Moves ,atching the same Product
        map to the same Tracking Item.
        Mapping one Stock Move to one Tracking Item causes wrong
        variance calculations since, for example,
        Stock Moves might be split or merged by Odoo logic.
        """
        tracking = super()._get_tracking_item()
        tracking = tracking.filtered(
            # For Stock Move, match Tracking Item that has a related Stock Move
            lambda x: (self.stock_move_id and x.stock_move_id)
            # or Tracking item matching the exact Work Order
            or (self.workorder_id and self.workorder_id == x.workorder_id)
        )
        # Keep only the first match
        return tracking[:1]
