# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("label")
    @api.depends_context("display_purchase_line_label")
    def _compute_display_name(self):
        if not self.env.context.get("display_purchase_line_label"):
            return super()._compute_display_name()
        for line in self:
            line.display_name = line.label or line.order_id.name
