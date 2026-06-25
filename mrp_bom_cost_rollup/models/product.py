# Copyright 2026 Cubiczan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_set_standard_price_from_bom(self):
        """Set the product cost from its (first) Bill of Materials rollup."""
        self.ensure_one()
        bom = (
            self.env["mrp.bom"]
            ._bom_find(products=self.product_variant_ids[:1])
            .get(self.product_variant_ids[:1])
        )
        if not bom:
            raise UserError(
                _(
                    "No Bill of Materials found for %(product)s.",
                    product=self.display_name,
                )
            )
        bom.action_set_standard_price_from_bom()
        return True
