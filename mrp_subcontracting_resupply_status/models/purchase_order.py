# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    resupply_status = fields.Selection(
        [
            ("pending", "Not Resupplied"),
            ("partial", "Partially Resupplied"),
            ("full", "Fully Resupplied"),
        ],
        compute="_compute_resupply_status",
        store=True,
    )

    @api.depends(
        "order_line",
        "order_line.move_ids",
        "order_line.move_ids.move_orig_ids.production_group_id",
    )
    def _compute_resupply_status(self):
        for order in self:
            resupplies = order._get_subcontracting_resupplies()
            if not resupplies or all(r.state == "cancel" for r in resupplies):
                order.resupply_status = False
            elif all(r.state in ["done", "cancel"] for r in resupplies):
                order.resupply_status = "full"
            elif any(r.state == "done" for r in resupplies):
                order.resupply_status = "partial"
            else:
                order.resupply_status = "pending"

    def _get_subcontracting_resupplies(self):
        """Get all resupply pickings for subcontract moves in this PO."""
        moves_subcontracted = self.order_line.move_ids.filtered(
            lambda m: m.is_subcontract
        )
        if not moves_subcontracted:
            return self.env["stock.picking"].browse()
        move_origs = moves_subcontracted.move_orig_ids
        if not move_origs:
            return self.env["stock.picking"].browse()
        result_pickings = move_origs.picking_id
        production_group_ids = move_origs.production_group_id
        if production_group_ids:
            all_pickings_with_prod_group = (
                self.env["stock.move"]
                .search([("production_group_id", "in", production_group_ids.ids)])
                .picking_id
            )
            result_pickings = result_pickings | all_pickings_with_prod_group
        resupply_route = self.env.ref(
            "mrp_subcontracting.route_resupply_subcontractor_mto",
            raise_if_not_found=False,
        )
        if not resupply_route:
            return result_pickings
        return result_pickings.filtered(
            lambda p: resupply_route in p.move_ids.product_id.route_ids
        )
