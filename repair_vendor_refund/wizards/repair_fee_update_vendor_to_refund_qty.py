# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RepairFeeUpdateVendorToRefundQty(models.TransientModel):
    _name = "repair.fee.update.vendor.to.refund.qty"
    _description = "Repair Fee Update Vendor To Refund Qty"

    vendor_to_refund_qty = fields.Float("Vendor Refund Qty")

    def button_confirm(self):
        if not self._context.get("active_ids"):
            return {"type": "ir.actions.act_window_close"}
        repair_fees = self.env["repair.fee"].browse(self._context["active_ids"])
        repair_fees.write({"vendor_to_refund_qty": self.vendor_to_refund_qty})
        return {"type": "ir.actions.act_window_close"}
