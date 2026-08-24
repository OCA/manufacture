#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def _get_move_raw_values(
        self,
        product,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        values = super()._get_move_raw_values(
            product,
            product_uom_qty,
            product_uom,
            operation_id=operation_id,
            bom_line=bom_line,
        )
        if bom_line:
            computed_quantity = bom_line._eval_quantity_formula(
                product,
                product_uom,
                product_uom_qty,
                self,
                operation_id=operation_id,
            )
            if computed_quantity is not None:
                values["product_uom_qty"] = computed_quantity
        return values
