# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("company_id", "bom_id", "product_id")
    def _compute_picking_type_id(self):
        res = super()._compute_picking_type_id()
        for mo in self:
            # Transfers and reservations already exist once the MO is confirmed,
            # so its operation type must not be repointed. A falsy state is a
            # record still being created (the field is precomputed).
            if mo.state and mo.state != "draft":
                continue
            if mo.product_id:
                base_domain = [
                    ("action", "=", "manufacture"),
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "child_of", mo.company_id.id),
                ]
                res_rule = self.env["procurement.group"]._search_rule(
                    False, False, mo.product_id, False, base_domain
                )
                if res_rule:
                    mo.picking_type_id = res_rule.picking_type_id
        return res
