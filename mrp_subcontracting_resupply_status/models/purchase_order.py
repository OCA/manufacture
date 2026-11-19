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

    @api.depends("order_line.move_ids.move_orig_ids.production_id.production_group_id")
    def _compute_resupply_status(self):
        for order in self:
            order.resupply_status = (
                self.env["stock.picking"]
                ._get_resupplies_of_subcontract_moves(order.order_line.move_ids)
                ._get_resupply_status()
            )
