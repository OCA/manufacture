# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # Skip picking_type_id as a onchange trigger, even though the
    # extended method is an onchange for picking_type_id too.
    # If triggered also from picking_type_id changes, it would be impossible
    # to adjust picking_type_id manually.
    @api.onchange("product_id", "company_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        if self.product_id:
            base_domain = [
                ("action", "=", "manufacture"),
                "|",
                ("company_id", "=", False),
                ("company_id", "child_of", self.company_id.id),
            ]
            res_rule = self.env["procurement.group"]._search_rule(
                False, self.product_id, False, base_domain
            )
            if res_rule:
                self.picking_type_id = res_rule.picking_type_id
        return res
