# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.constrains("product_id")
    def _check_product_is_kit(self):
        """Do not allow inventory adjustments for kits"""
        for line in self:
            inventory_company_id = line.inventory_id.company_id
            if line.product_id.allow_kit_inventory:
                continue
            bom = self.env["mrp.bom"]._bom_find(
                product=line.product_id,
                company_id=inventory_company_id.id,
                bom_type="phantom",
            )
            if len(bom):
                raise ValidationError(
                    _(
                        "Inventory adjustment for a kit is not allowed. Kit found"
                        "for %s and company %s"
                        % (bom.product_tmpl_id.display_name, inventory_company_id.name,)
                    )
                )
