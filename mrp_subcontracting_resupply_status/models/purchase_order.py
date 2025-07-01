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

    @api.depends("order_line.move_ids.move_orig_ids.production_id.picking_ids.state")
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
