# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        """Prepare manufacturing order values.
        
        Extends the base method to include source procurement group information
        when creating manufacturing orders.
        
        Args:
            product_id: Product to manufacture
            product_qty: Quantity to manufacture
            product_uom: Unit of measure
            location_id: Location for manufacturing
            name: Manufacturing order name
            origin: Origin reference
            company_id: Company ID
            values: Additional values
            bom: Bill of materials
            
        Returns:
            dict: Manufacturing order values
        """
        res = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        res["source_procurement_group_id"] = (
            values.get("group_id").id if values.get("group_id", False) else False
        )
        return res