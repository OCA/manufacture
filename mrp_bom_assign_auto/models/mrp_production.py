# Copyright 2026 Studio73 - Miguel Gandia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "product_id",
        "never_product_template_attribute_value_ids",
        "product_qty",
        "product_uom_id",
        "location_src_id",
        "picking_type_id",
    )
    def _compute_bom_id(self):
        productions_by_context = defaultdict(lambda: self.env["mrp.production"])
        productions_without_product = self.filtered(
            lambda production: not production.product_id
        )
        for production in self - productions_without_product:
            product = production.product_id
            uom = production.product_uom_id or product.uom_id
            quantity = uom._compute_quantity(
                production.product_qty, product.uom_id, round=False
            )
            location = (
                production.location_src_id
                or production.picking_type_id.default_location_src_id
            )
            key = (product.id, quantity, location.id, production.company_id.id)
            productions_by_context[key] |= production

        if productions_without_product:
            super(MrpProduction, productions_without_product)._compute_bom_id()

        for production_group in productions_by_context.values():
            production = production_group[0]
            product = production.product_id
            uom = production.product_uom_id or product.uom_id
            quantity = uom._compute_quantity(
                production.product_qty, product.uom_id, round=False
            )
            context = {
                "mrp_bom_assign_auto_quantities": {product.id: quantity},
            }
            location = (
                production.location_src_id
                or production.picking_type_id.default_location_src_id
            )
            if location:
                context["location"] = location.id
            super(
                MrpProduction, production_group.with_context(**context)
            )._compute_bom_id()
        return
