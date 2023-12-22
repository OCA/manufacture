# Copyright 2023 Camptocamp  (https://www.camptocamp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpMultiLevel(models.TransientModel):
    _inherit = "mrp.multi.level"

    def _get_safety_stock_target_date(self, product_mrp_area):
        """get the date at which the safety stock rebuild should be targeted,
        taking the stress period into account"""
        target = super()._get_safety_stock_target_date(product_mrp_area)
        return max(product_mrp_area.safety_stock_target_date, target)

    def _get_qty_to_order(self, product_mrp_area, date, move_qty, onhand):
        # when in the stress period, don't reconstruct the safety stock
        qty = super()._get_qty_to_order(product_mrp_area, date, move_qty, onhand)
        if date < self._get_safety_stock_target_date(product_mrp_area):
            qty -= product_mrp_area.mrp_minimum_stock
        return qty
