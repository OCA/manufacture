# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class RepairPurchaseReturnWiz(models.TransientModel):
    _name = "repair.purchase.return.wiz"
    _description = "RepairPurchaseReturnWizard"

    vendor_id = fields.Many2one("res.partner", required=True)

    @api.model
    def default_get(self, fields):
        vals = super(RepairPurchaseReturnWiz, self).default_get(fields)
        repair_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]

        if not repair_ids:
            return vals
        assert active_model == "repair.order", "Bad context propagation"

        repairs = self.env["repair.order"].browse(repair_ids)
        vendors = self.env["res.partner"]
        for repair in repairs:
            vendors |= (
                repair.product_id.mapped("seller_ids")
                .filtered(lambda s: s.company_id == repair.company_id)
                .partner_id
            )
        if len(vendors) >= 1:
            vals["vendor_id"] = vendors[0].id
        return vals

    def create_purchase_returns(self):
        repairs = self.env["repair.order"].browse(self._context.get("active_ids", []))
        for repair in repairs:
            repair._create_purchase_return(self.vendor_id)
        if self._context.get("open_purchase_returns", False):
            return repairs.action_view_purchase_returns()
        return {"type": "ir.actions.act_window_close"}
