# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import api, models
from odoo.tools import config, float_compare


class MrpBom(models.Model):
    _inherit = "mrp.bom"

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
        params = self.env["ir.config_parameter"].sudo()
        bom_available = defaultdict(lambda: self.env["mrp.bom"])
        domain = self._bom_find_domain(
            products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        boms = self.search(domain, order="sequence, product_id, id")
        bom_products = list(set(boms.bom_line_ids.mapped("product_id").ids))
        type_stock_check = params.get_param(
            "mrp_bom_assign_auto.bom_stock_check", "free_qty"
        )
        product_available = (
            self.env["product.product"].browse(bom_products).read([type_stock_check])
        )
        product_available_map = {
            rec["id"]: rec[type_stock_check] for rec in product_available
        }
        for bom in boms:
            for line in bom.bom_line_ids:
                required = line.product_qty
                component = line.product_id
                available = product_available_map.get(line.product_id.id)
                if (
                    float_compare(
                        available,
                        required,
                        precision_rounding=component.uom_id.rounding,
                    )
                    < 0
                ):
                    break
                bom_available[products] = bom
        if not any(bom_available.values()):
            return super()._bom_find(
                products,
                picking_type=picking_type,
                company_id=company_id,
                bom_type=bom_type,
            )
        return bom_available
