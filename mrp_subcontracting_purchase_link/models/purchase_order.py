# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    subcontract_production_ids = fields.One2many(
        "mrp.production",
        "purchase_order_id",
        "Subcontract Production Orders",
        readonly=True,
    )
    subcontract_production_count = fields.Integer(
        compute="_compute_subcontract_production_count"
    )

    def action_view_mrp(self):
        productions = self.subcontract_production_ids
        action = self.env.ref("mrp.mrp_production_action").read()[0]
        if len(productions) > 1:
            action["domain"] = [("id", "in", productions.ids)]
        elif len(productions) == 1:
            action["views"] = [
                (self.env.ref("mrp.mrp_production_form_view").id, "form")
            ]
            action["res_id"] = productions.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def _compute_subcontract_production_count(self):
        for order in self:
            order.subcontract_production_count = len(order.subcontract_production_ids)
