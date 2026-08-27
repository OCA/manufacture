# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_bom_lines(self, bom=None):
        """Get BoM lines recursively for the product."""
        bom_lines_ids = self.bom_ids.bom_line_ids.ids
        if not bom:
            bom = self.env["mrp.bom"]
        bom |= self.bom_ids
        if len(self.bom_ids.bom_line_ids.product_id.bom_ids - bom) > 0:
            bom_lines_ids += self.bom_ids.bom_line_ids.product_id.get_bom_lines(bom)
        return bom_lines_ids

    def button_bom_allergens(self):
        """Button to compute allergens from BoM."""
        for product in self:
            bom_lines_ids = product.get_bom_lines()
            bom_lines = self.env["mrp.bom.line"].browse(bom_lines_ids)
            if bom_lines:
                all_allergens = bom_lines.product_id.allergen_ids
                product.allergen_ids = all_allergens
            else:
                product.allergen_ids = False
