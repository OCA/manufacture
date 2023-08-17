# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class PurchaseReturnOrder(models.Model):
    _inherit = "purchase.return.order"

    repair_order_count = fields.Integer(
        compute="_compute_repair_orders",
        string="Repair Orders Count",
    )
    repair_order_ids = fields.Many2many(
        comodel_name="repair.order",
        compute="_compute_repair_orders",
    )

    @api.depends(
        "order_line.repair_line_ids.repair_id",
        "order_line.repair_fee_ids.repair_id",
    )
    def _compute_repair_orders(self):
        for rec in self:
            repair_orders = rec.order_line.mapped("repair_line_ids.repair_id")
            repair_orders |= rec.order_line.mapped("repair_fee_ids.repair_id")
            rec.repair_order_ids = repair_orders
            rec.repair_order_count = len(repair_orders)

    def action_view_repair_orders(self):
        repair_orders = self.mapped("repair_order_ids")
        action = self.env["ir.actions.actions"]._for_xml_id(
            "repair.action_repair_order_tree"
        )
        if len(repair_orders) > 1:
            action["domain"] = [("id", "in", repair_orders.ids)]
        elif len(repair_orders) == 1:
            form_view = [(self.env.ref("repair.view_repair_order_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = repair_orders.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
