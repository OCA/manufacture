# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def write(self, vals):
        # Saving the form after changing the quantity producing writes the
        # recomputed component quantities in the same write.
        if "qty_producing" in vals:
            return super(
                MrpProduction, self.with_context(mrp_set_qty_producing=True)
            ).write(vals)
        return super().write(vals)

    def _set_qty_producing(self, pick_manual_consumption_moves=True):
        return super(
            MrpProduction, self.with_context(mrp_set_qty_producing=True)
        )._set_qty_producing(
            pick_manual_consumption_moves=pick_manual_consumption_moves
        )
