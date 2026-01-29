# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        """Trigger recomputation of resupply_status when resupply moves change state."""
        res = super().write(vals)

        if "state" not in vals:
            return res

        # Get resupply route once for efficiency
        resupply_route = self.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto",
            raise_if_not_found=False,
        )
        if not resupply_route:
            return res

        # Check if any affected moves are in a resupply picking
        has_resupply = any(
            move.picking_id and resupply_route in move.product_id.route_ids
            for move in self
        )

        if not has_resupply:
            return res

        # Recompute all receipts and POs with pending/partial status
        receipts = self.env["stock.picking"].search(
            [
                ("picking_type_id.code", "=", "incoming"),
                ("move_ids.move_orig_ids", "!=", False),
                ("resupply_status", "!=", False),
            ]
        )
        if receipts:
            receipts._compute_resupply_status()

        pos = self.env["purchase.order"].search(
            [
                ("order_line.move_ids.is_subcontract", "=", True),
                ("resupply_status", "!=", False),
            ]
        )
        if pos:
            pos._compute_resupply_status()

        return res
