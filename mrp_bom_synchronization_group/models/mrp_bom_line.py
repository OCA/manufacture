# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

SYNC_TRIGGER_FIELDS = {
    "product_id",
    "product_qty",
    "product_uom_id",
    "bom_product_template_attribute_value_ids",
}


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        if not self.env.context.get("skip_bom_component_sync"):
            lines.bom_id._propagate_components_to_group()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get(
            "skip_bom_component_sync"
        ) and SYNC_TRIGGER_FIELDS.intersection(vals):
            self.bom_id._propagate_components_to_group()
        return res

    def unlink(self):
        boms = self.bom_id
        res = super().unlink()
        if not self.env.context.get("skip_bom_component_sync"):
            boms._propagate_components_to_group()
        return res
