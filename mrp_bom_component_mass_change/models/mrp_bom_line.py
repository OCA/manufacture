# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    component_in_multiple_boms = fields.Boolean(
        compute="_compute_component_in_multiple_boms",
    )

    @api.depends("product_id")
    def _compute_component_in_multiple_boms(self):
        products = self.product_id
        bom_counts = {}
        if products:
            groups = self.env["mrp.bom.line"].read_group(
                [("product_id", "in", products.ids)],
                ["bom_id:count_distinct"],
                ["product_id"],
            )
            bom_counts = {group["product_id"][0]: group["bom_id"] for group in groups}
        for line in self:
            line.component_in_multiple_boms = bom_counts.get(line.product_id.id, 0) > 1

    def action_bom_component_mass_change(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_bom_component_mass_change.mrp_bom_component_mass_change_action"
        )
        action["context"] = {
            "default_component_id": self.product_id.id,
            "default_component_locked": True,
        }
        return action
