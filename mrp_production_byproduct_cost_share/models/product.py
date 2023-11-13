# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_bom_count(self):
        for product in self:
            super()._compute_bom_count()
            product.bom_count += self.env["mrp.bom"].search_count(
                [("byproduct_ids.product_id.product_tmpl_id", "=", product.id)]
            )


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_bom_count(self):
        for product in self:
            super()._compute_bom_count()
            product.bom_count += self.env["mrp.bom"].search_count(
                [("byproduct_ids.product_id", "=", product.id)]
            )

    def _set_price_from_bom(self, boms_to_recompute=False):
        super()._set_price_from_bom(boms_to_recompute=False)
        byproduct_bom = self.env["mrp.bom"].search(
            [("byproduct_ids.product_id", "=", self.id)],
            order="sequence, product_id, id",
            limit=1,
        )
        if byproduct_bom:
            price = self._compute_bom_price(
                byproduct_bom, boms_to_recompute=boms_to_recompute, byproduct_bom=True
            )
            if price:
                self.standard_price = price

    def _compute_bom_price(self, bom, boms_to_recompute=False, byproduct_bom=False):
        price = super()._compute_bom_price(bom, boms_to_recompute)
        if byproduct_bom:
            byproduct_lines = bom.byproduct_ids.filtered(
                lambda b: b.product_id == self and b.cost_share != 0
            )
            product_uom_qty = 0
            for line in byproduct_lines:
                product_uom_qty += line.product_uom_id._compute_quantity(
                    line.product_qty, self.uom_id, round=False
                )
            byproduct_cost_share = sum(byproduct_lines.mapped("cost_share"))
            if byproduct_cost_share and product_uom_qty:
                return price * byproduct_cost_share / 100
        else:
            byproduct_cost_share = sum(bom.byproduct_ids.mapped("cost_share"))
            if byproduct_cost_share:
                price *= float_round(
                    1 - byproduct_cost_share / 100, precision_rounding=0.0001
                )
            return price

    def action_view_bom(self):
        action = super().action_view_bom()
        template_ids = self.mapped("product_tmpl_id").ids
        action["domain"] = [
            "|",
            "|",
            ("byproduct_ids.product_id", "in", self.ids),
            ("product_id", "in", self.ids),
            "&",
            ("product_id", "=", False),
            ("product_tmpl_id", "in", template_ids),
        ]
        return action
