# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("company_id", "bom_id", "product_id")
    def _compute_picking_type_id(self):
        res = super()._compute_picking_type_id()
        for mo in self:
            if mo.product_id:
                picking_type = self._get_picking_type_from_route(
                    mo.product_id, mo.company_id.id
                )
                if picking_type:
                    mo.picking_type_id = picking_type
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # `mrp.production.create` assigns the default operation type and takes the
        # order reference from its sequence before the compute can run, so the route
        # has to be resolved here as well to keep both of them consistent.
        for vals in vals_list:
            if vals.get("picking_type_id") or not vals.get("product_id"):
                continue
            product = self.env["product.product"].browse(vals["product_id"])
            company_id = vals.get("company_id") or self.env.company.id
            picking_type = self._get_picking_type_from_route(product, company_id)
            if picking_type:
                vals["picking_type_id"] = picking_type.id
        return super().create(vals_list)

    @api.model
    def _get_picking_type_from_route(self, product, company_id):
        """Return the operation type of the manufacture rule found for the product."""
        domain = [
            ("action", "=", "manufacture"),
            "|",
            ("company_id", "=", False),
            ("company_id", "child_of", company_id),
        ]
        rule = self.env["procurement.group"]._search_rule(
            False, False, product, False, domain
        )
        return rule.picking_type_id
