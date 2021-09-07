# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RepairLineUpdateVendorToRefundQty(models.TransientModel):
    _name = "repair.line.update.vendor.to.refund.qty"
    _description = "Repair Line Update Vendor To Refund Qty"

    vendor_to_refund_qty = fields.Float("Vendor Refund Qty")

    def button_confirm(self):
        if not self._context.get("active_ids"):
            return {"type": "ir.actions.act_window_close"}
        repair_lines = self.env["repair.line"].browse(self._context["active_ids"])
        repair_lines.write({"vendor_to_refund_qty": self.vendor_to_refund_qty})
        return {"type": "ir.actions.act_window_close"}
