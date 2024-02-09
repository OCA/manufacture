# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def stock_price_unit_sync(self):
        for line in self.filtered(lambda l: l.state in ["purchase", "done"]):
            move_ids = line.move_ids
            if move_ids.is_subcontract and move_ids.move_orig_ids.production_id:
                changes_price = line._get_stock_move_price_unit()
                price_unit = (
                    move_ids.move_orig_ids.price_unit
                    - move_ids.price_unit
                    + changes_price
                )
                move_ids.move_orig_ids.write({"price_unit": price_unit})
                svls = (
                    move_ids.move_orig_ids.sudo()
                    .mapped("stock_valuation_layer_ids")
                    .filtered(
                        # Filter children SVLs (like landed cost)
                        lambda x: not x.stock_valuation_layer_id
                    )
                )
                svls.write(
                    {
                        "unit_cost": price_unit,
                    }
                )
        return super().stock_price_unit_sync()
