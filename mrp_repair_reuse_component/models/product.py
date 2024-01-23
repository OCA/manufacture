# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _count_returned_sn_products(self, sn_lot):
        """Consider repair lines where:

        - Product was added into another
        - Product was removed in a destination that is not internal
        """
        res = self.env["repair.line"].search_count(
            [
                ("type", "=", "add"),
                ("product_uom_qty", "=", 1),
                ("lot_id", "=", sn_lot.id),
                ("state", "=", "done"),
                ("location_dest_id.usage", "=", "production"),
            ]
        ) - self.env["repair.line"].search_count(
            [
                ("type", "=", "remove"),
                ("product_uom_qty", "=", 1),
                ("lot_id", "=", sn_lot.id),
                ("state", "=", "done"),
                ("location_dest_id.usage", "!=", "internal"),
            ]
        )
        return super()._count_returned_sn_products(sn_lot) - res
