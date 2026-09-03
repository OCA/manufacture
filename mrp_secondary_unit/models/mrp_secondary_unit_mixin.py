# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpSecondaryUnitMixin(models.AbstractModel):
    _name = "mrp.secondary.unit.mixin"
    _inherit = "product.secondary.unit.mixin"
    _description = "MRP Secondary Unit Mixin"
    _secondary_unit_fields = {
        "qty_field": "product_qty",
        "uom_field": "product_uom_id",
    }

    @api.model
    def _get_default_value_for_qty_field(self):
        return 1.0

    @api.model
    def _get_secondary_uom_qty_depends(self):
        # The factor refers to the unit of the product, so the secondary
        # quantity has to be converted again when the unit of the line changes.
        return super()._get_secondary_uom_qty_depends() + ["product_uom_id"]

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_qty(self):
        for record in self:
            if record.secondary_uom_id and not record.secondary_uom_qty:
                record._onchange_helper_product_uom_for_secondary()
        self._compute_helper_target_field_qty()
