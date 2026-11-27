# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_generate_serial(self, workorder=False):
        self.ensure_one()
        action = super().action_generate_serial(workorder=workorder)
        if self.product_tracking == "lot":
            for move_byproduct in self.move_byproduct_ids.filtered(
                lambda move: move.byproduct_id.inherit_lot
            ):
                move_lines = move_byproduct.move_line_ids
                if len(move_lines) != 1 or move_lines.lot_id:
                    continue
                lot = self._generate_byproduct_lot(move_byproduct.byproduct_id)
                if lot:
                    move_lines.lot_id = lot
        return action

    def _generate_byproduct_lot(self, byproduct):
        if byproduct.product_id.tracking == "none":
            return self.env["stock.lot"]
        self.lot_producing_ids.ensure_one()
        lot = self.env["stock.lot"].search(
            [
                ("name", "=", self.lot_producing_ids.name),
                ("product_id", "=", byproduct.product_id.id),
                ("company_id", "in", [False, self.company_id.id]),
            ],
            limit=1,
        )
        if lot:
            return lot
        return self.lot_producing_ids.copy(
            {
                "product_id": byproduct.product_id.id,
                "name": self.lot_producing_ids.name,
                "company_id": self.company_id.id,
            }
        )
