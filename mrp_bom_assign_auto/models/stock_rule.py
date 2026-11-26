# Copyright 2026 Studio73 - Miguel Gandia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from collections import defaultdict

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def run(self, procurements, raise_user_error=True):
        quantities = defaultdict(float)
        locations = defaultdict(set)
        for procurement in procurements:
            if procurement.product_uom.compare(procurement.product_qty, 0) <= 0:
                continue
            product = procurement.product_id
            quantities[product.id] += procurement.product_uom._compute_quantity(
                procurement.product_qty, product.uom_id, round=False
            )
            warehouse = procurement.values.get("warehouse_id")
            if isinstance(warehouse, int):
                warehouse = self.env["stock.warehouse"].browse(warehouse)
            if warehouse and warehouse.lot_stock_id:
                locations[product.id].add(warehouse.lot_stock_id.id)

        context = dict(self.env.context)
        if quantities:
            context["mrp_bom_assign_auto_quantities"] = dict(quantities)
            context["mrp_bom_assign_auto_locations"] = {
                product_id: next(iter(product_locations))
                for product_id, product_locations in locations.items()
                if len(product_locations) == 1
            }
        return super(StockRule, self.with_context(**context)).run(
            procurements, raise_user_error=raise_user_error
        )
