# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        """Include packaging in new move values."""
        result = super()._get_move_raw_values(
            product_id,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            bom_line=bom_line,
        )
        if bom_line and bom_line.product_packaging_id:
            result["product_packaging_id"] = bom_line.product_packaging_id.id
        return result
