# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    product_allergen_ids = fields.Many2many(
        "allergen.allergen", string="Allergens", compute="_compute_product_allergen_ids"
    )

    def _compute_product_allergen_ids(self):
        for line in self:
            line.product_allergen_ids = line.product_id.allergen_ids
