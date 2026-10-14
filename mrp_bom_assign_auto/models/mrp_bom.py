# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import api, models
from odoo.tools import config, float_compare


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    _STOCK_CHECKS = {"free_qty", "virtual_available"}

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        test_condition = config["test_enable"] and not self.env.context.get(
            "test_mrp_bom_assign_auto"
        )
        if test_condition or self.env.context.get("no_mrp_bom_assign_auto"):
            return super()._bom_find(
                products,
                picking_type=picking_type,
                company_id=company_id,
                bom_type=bom_type,
            )
        products = products.filtered(lambda product: product.type != "service")
        if not products:
            return defaultdict(lambda: self.env["mrp.bom"])
        params = self.env["ir.config_parameter"].sudo()
        domain = self._bom_find_domain(
            products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        boms = self.search(domain, order="sequence, product_id, id")
        if not boms:
            return super()._bom_find(
                products,
                picking_type=picking_type,
                company_id=company_id,
                bom_type=bom_type,
            )
        bom_available = defaultdict(lambda: self.env["mrp.bom"])
        bom_products = boms.bom_line_ids.product_id.filtered("is_storable")
        type_stock_check = params.get_param(
            "mrp_bom_assign_auto.bom_stock_check", "free_qty"
        )
        if type_stock_check not in self._STOCK_CHECKS:
            type_stock_check = "free_qty"
        stock_context = self._get_stock_context(products, picking_type)
        product_available = bom_products.with_context(**stock_context).read(
            [type_stock_check]
        )
        product_available_map = {
            rec["id"]: rec.get(type_stock_check, 0.0) for rec in product_available
        }

        for product in products:
            for bom in boms:
                if bom.product_id and bom.product_id != product:
                    continue
                if (
                    not bom.product_id
                    and bom.product_tmpl_id != product.product_tmpl_id
                ):
                    continue
                if self._bom_is_available(bom, product, product_available_map):
                    bom_available[product] = bom
                    break

        products_without_bom = products.filtered(
            lambda product: product not in bom_available
        )
        if products_without_bom:
            bom_available.update(
                super()._bom_find(
                    products_without_bom,
                    picking_type=picking_type,
                    company_id=company_id,
                    bom_type=bom_type,
                )
            )
        return bom_available

    def _get_stock_context(self, products, picking_type):
        context = dict(self.env.context)
        locations = context.get("mrp_bom_assign_auto_locations", {})
        location_ids = {
            locations.get(product.id)
            for product in products
            if locations.get(product.id)
        }
        if not context.get("location") and len(location_ids) == 1:
            context["location"] = location_ids.pop()
        if not context.get("location") and picking_type:
            picking_type = picking_type[:1]
            if picking_type.default_location_src_id:
                context["location"] = picking_type.default_location_src_id.id
        context["no_mrp_bom_assign_auto"] = True
        return context

    def _get_demand_quantity(self, product):
        quantities = self.env.context.get("mrp_bom_assign_auto_quantities", {})
        if not isinstance(quantities, dict):
            return None
        return quantities.get(product.id, quantities.get(str(product.id)))

    def _bom_is_available(self, bom, product, product_available_map):
        demand_quantity = self._get_demand_quantity(product)
        quantity_factor = 1.0
        if demand_quantity is not None:
            demand_quantity = product.uom_id._compute_quantity(
                demand_quantity, bom.product_uom_id, round=False
            )
            quantity_factor = demand_quantity / (bom.product_qty or 1.0)

        for line in bom.bom_line_ids:
            component = line.product_id
            if not component.is_storable:
                continue
            required = line.product_uom_id._compute_quantity(
                line.product_qty * quantity_factor,
                component.uom_id,
                round=False,
            )
            if component.uom_id.is_zero(required):
                continue
            if (
                float_compare(
                    product_available_map.get(component.id, 0.0),
                    required,
                    precision_rounding=component.uom_id.rounding,
                )
                < 0
            ):
                return False
        return True
