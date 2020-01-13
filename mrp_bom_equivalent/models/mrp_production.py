# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, _


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_product_search_criteria(self, bom_line):
        return [
            (
                "equivalent_categ_id",
                "=",
                bom_line.product_id.equivalent_categ_id.id,
            )
        ]

    def _get_product_equivalent(self, bom_line, requested_qty):
        # get all the other products in the same product category
        ProductProduct = self.env["product.product"]
        StockQuant = self.env["stock.quant"]
        product_ids = ProductProduct.search(
            self._get_product_search_criteria(bom_line),
            order="priority asc, id asc",
        )
        # exclude the non-equivalent parts listed in the BOM line and the
        # current product
        product_ids -= bom_line.nonequivalent_product_ids + bom_line.product_id
        product_eq = False
        for product_id in product_ids:
            qty_available = StockQuant._get_available_quantity(
                product_id, self.location_src_id
            )
            if qty_available >= requested_qty:
                product_eq = product_id
                break
        return product_eq

    def _get_raw_move_data(self, bom_line, line_data):
        ProductProduct = self.env["product.product"]
        StockQuant = self.env["stock.quant"]
        res = super(MrpProduction, self)._get_raw_move_data(
            bom_line, line_data
        )
        if not bom_line.use_equivalences:
            return res

        qty_available = StockQuant._get_available_quantity(
            bom_line.product_id, self.location_src_id
        )
        if qty_available < line_data["qty"]:
            product_equivalent = self._get_product_equivalent(
                bom_line, line_data["qty"]
            )
            if product_equivalent:
                body = _(
                    "%s has been replaced by %s."
                    % (
                        ProductProduct.browse(
                            res.get("product_id")
                        ).name_get()[0][1],
                        product_equivalent.name_get()[0][1],
                    )
                )
                res.update(
                    {
                        "product_id": product_equivalent.id,
                        "price_unit": product_equivalent.standard_price,
                    }
                )
                self.message_post(body=body)
        return res
