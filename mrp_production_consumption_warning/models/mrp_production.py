# Copyright 2023 Komit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.tools import float_compare


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    consumption_warning_msg = fields.Text(compute="_compute_consumption_warning_msg")

    @api.depends(
        "bom_id",
        "bom_id.bom_line_ids",
        "bom_id.bom_line_ids.product_id",
        "bom_id.bom_line_ids.product_qty",
        "move_raw_ids",
        "move_raw_ids.product_id",
        "move_raw_ids.product_uom_qty",
    )
    def _compute_consumption_warning_msg(self):
        for rec in self:
            rec.consumption_warning_msg = rec._get_consumption_warning_msg()

    def _get_consumption_warning_msg(self):
        self.ensure_one()
        if not self.bom_id or not self.bom_id.bom_line_ids:
            return ""

        expected_qty_by_product = self._get_expected_qty_by_product()
        actual_qty_by_product = self._get_actual_qty_by_product()

        unused_products = self.env["product.product"]
        unpresent_products = self.env["product.product"]
        wrong_quantity_msg = ""

        for product, expected_qty in expected_qty_by_product.items():
            actual_qty = actual_qty_by_product.get(product)
            if actual_qty is None:
                unused_products |= product
                continue

            rounding = product.uom_id.rounding
            if (
                float_compare(expected_qty, actual_qty, precision_rounding=rounding)
                != 0
            ):
                wrong_quantity_msg += _(
                    "- The MO line quantity for Product %(product)s is %(w_qty)s "
                    "while the quantity of %(r_qty)s (%(qty_per_1)s x %(product_qty)s) "
                    "is expected from the BoM line\n",
                    product=product.display_name,
                    w_qty=actual_qty,
                    r_qty=expected_qty,
                    qty_per_1=expected_qty / self.product_qty,
                    product_qty=self.product_qty,
                )

        for product in actual_qty_by_product:
            if product not in expected_qty_by_product:
                unpresent_products |= product

        message = ""
        if unused_products:
            message += _(
                "- The MO does not use the product(s) %(names)s\n",
                names=", ".join(unused_products.mapped("display_name")),
            )
        message += wrong_quantity_msg
        if unpresent_products:
            message += _(
                "- The components %(names)s is/are not present on the BoM\n",
                names=", ".join(unpresent_products.mapped("display_name")),
            )
        if message:
            message = (
                "There are discrepancies between your Manufacturing Order and "
                "the BoM associated with the Finished products:\n" + message
            )
        return message

    def _get_expected_qty_by_product(self):
        qty_by_product = defaultdict(float)
        for move_values in self._get_moves_raw_values():
            product = self.env["product.product"].browse(move_values["product_id"])
            qty_by_product[product] += move_values["product_uom_qty"]
        return qty_by_product

    def _get_actual_qty_by_product(self):
        qty_by_product = defaultdict(float)
        for move in self.move_raw_ids:
            qty_by_product[move.product_id] += move.product_uom_qty
        return qty_by_product
