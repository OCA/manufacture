# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # Just to add the manufacturing triggers to the base module's compute
    @api.depends(
        "raw_material_production_id.owner_id",
        "production_id",
        "move_dest_ids.raw_material_production_id.owner_id",
        "consume_unbuild_id.mo_id.owner_id",
        "unbuild_id.mo_id.owner_id",
    )
    def _compute_restricted_owner_id(self):
        return super()._compute_restricted_owner_id()

    def _get_mo_to_unbuild(self):
        self.ensure_one()
        return self.consume_unbuild_id.mo_id or self.unbuild_id.mo_id

    def _get_owner_for_assign(self):
        self.ensure_one()
        if self.raw_material_production_id:
            return self.raw_material_production_id.owner_id
        # Manufactured product should not consider the owner for assignment, or the
        # result might be messed up (e.g. tries to move stock from the internal location
        # instead of the production location).
        if self.production_id:
            return self.env["res.partner"]
        # For chained origin moves for production component moves.
        production = self.move_dest_ids.raw_material_production_id
        if production:
            return production.owner_id
        mo_to_unbuild = self._get_mo_to_unbuild()
        if mo_to_unbuild:
            return mo_to_unbuild.owner_id
        return super()._get_owner_for_assign()
