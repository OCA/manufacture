# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.depends(
        "product_id.mrp_production_request_ids",
        "product_id.mrp_production_request_ids.state",
    )
    def _compute_qty(self):
        """Extend to add more depends values"""
        return super()._compute_qty()

    def _quantity_in_progress(self):
        res = super()._quantity_in_progress()
        mrp_requests = self.env["mrp.production.request"].search(
            [("state", "not in", ("done", "cancel")), ("orderpoint_id", "in", self.ids)]
        )
        for rec in mrp_requests:
            res[rec.orderpoint_id.id] += rec.product_uom_id._compute_quantity(
                rec.pending_qty, rec.orderpoint_id.product_uom, round=False
            )
        return res
