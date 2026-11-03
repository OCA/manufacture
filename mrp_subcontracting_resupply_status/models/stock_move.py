# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            self._recompute_subcontracting_resupply_status()
        return res

    def _recompute_subcontracting_resupply_status(self):
        """Trigger the resupply status of the receipts and purchase orders
        related to the resupply moves in self."""
        resupply_moves = self.filtered(
            lambda m: m.production_group_id and m.location_dest_id.is_subcontract()
        )
        if not resupply_moves:
            return
        productions = resupply_moves.production_group_id.production_ids
        receipt_moves = productions.move_finished_ids.move_dest_ids.filtered(
            "is_subcontract"
        )
        self.env.add_to_compute(
            self.env["stock.picking"]._fields["resupply_status"],
            receipt_moves.picking_id,
        )
        self.env.add_to_compute(
            self.env["purchase.order"]._fields["resupply_status"],
            receipt_moves.purchase_line_id.order_id,
        )
