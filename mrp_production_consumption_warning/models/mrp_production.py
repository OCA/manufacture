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
            rec.consumption_warning_msg = ""
            if not rec.bom_id or not rec.bom_id.bom_line_ids:
                continue

            unused_products = self.env["product.product"]
            wrong_quantity_msg = ""
            unpresent_products = self.env["product.product"]

            expected_move_values = rec._get_moves_raw_values()
            expected_qty_by_product = defaultdict(float)
            for move_values in expected_move_values:
                move_product = self.env["product.product"].browse(
                    move_values["product_id"]
                )
                expected_qty_by_product[move_product] += move_values["product_uom_qty"]

            actual_qty_by_product = defaultdict(float)
            for move in rec.move_raw_ids:
                actual_qty_by_product[move.product_id] += move.product_uom_qty

            for product, qty in expected_qty_by_product.items():
                if not actual_qty_by_product.get(product):
                    unused_products |= product
                    continue
                rounding = product.uom_id.rounding
                if (
                    float_compare(
                        qty,
                        actual_qty_by_product.get(product),
                        precision_rounding=rounding,
                    )
                    != 0
                ):
                    wrong_quantity_msg += _(
                        "- The MO line quantity for Product %(product)s is %(w_qty)s "
                        "while the quantity of %(r_qty)s (%(qty_per_1)s x %(product_qty)s) "
                        "is expected from the BoM line\n",
                        product=", ".join(product.mapped(lambda x: x.display_name)),
                        w_qty=actual_qty_by_product.get(product),
                        r_qty=qty,
                        qty_per_1=qty / rec.product_qty,
                        product_qty=rec.product_qty,
                    )

            for product in actual_qty_by_product:
                if not expected_qty_by_product.get(product):
                    unpresent_products |= product

            if unused_products:
                rec.consumption_warning_msg += _(
                    "- The MO does not use the product(s) %(names)s\n",
                    names=", ".join(unused_products.mapped(lambda x: x.display_name)),
                )
            rec.consumption_warning_msg += wrong_quantity_msg
            if unpresent_products:
                rec.consumption_warning_msg += _(
                    "- The components %(names)s is/are not present on the BoM\n",
                    names=", ".join(product.mapped(lambda x: x.display_name)),
                )
            if rec.consumption_warning_msg != "":
                rec.consumption_warning_msg = (
                    "There are discrepancies between your Manufacturing Order and "
                    "the BoM associated with the Finished products:\n"
                    + rec.consumption_warning_msg
                )
