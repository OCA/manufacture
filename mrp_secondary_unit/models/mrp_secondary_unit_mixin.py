# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpSecondaryUnitMixin(models.AbstractModel):
    _name = "mrp.secondary.unit.mixin"
    _inherit = "product.secondary.unit.mixin"
    _description = "MRP Secondary Unit Mixin"

    def _compute_helper_target_field_qty(self):
        """Derive a secondary quantity still at zero before converting it back.

        The conversion drops the pending recompute of the secondary quantity
        before reading it, so picking a secondary unit on a quantity that was
        typed first would read it as zero and reset that quantity. Deriving it
        from the quantity first is what the unit is picked for anyway.
        """
        for record in self:
            if record.secondary_uom_id and not record.secondary_uom_qty:
                record._onchange_helper_product_uom_for_secondary()
        return super()._compute_helper_target_field_qty()
