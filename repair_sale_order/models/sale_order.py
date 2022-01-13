# Copyright 2022 ForgeFlow S.L. (https://forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):

    _inherit = "sale.order"

    repair_order_ids = fields.Many2many(
        comodel_name="repair.order",
        string="Repair orders",
        compute="_compute_repair_order",
    )
    repair_order_count = fields.Integer(
        string="Repair orders count",
        compute="_compute_repair_order",
    )

    def _compute_repair_order(self):
        for rec in self:
            rec.repair_order_ids = rec.mapped(
                "order_line.repair_line_ids.repair_id"
            ).ids
            rec.repair_order_count = len(rec.repair_order_ids)

    def action_show_repair_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "repair.action_repair_order_tree"
        )
        form_view = [(self.env.ref("repair.view_repair_order_form").id, "form")]
        orders = self.mapped("repair_order_ids")
        if len(orders) == 1:
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = orders.ids[0]
        else:
            action["domain"] += [("id", "in", orders.ids)]
            domain = safe_eval(action["domain"]) or []
            domain += [("id", "in", orders.ids)]
            action["domain"] = action["domain"]
        return action

    def _change_repair_order_status_done(self):
        for repair_order in self.mapped("repair_order_ids"):
            repair_order.write(
                {
                    "state": "done",
                }
            )

    def _change_repair_order_status_confirmed(self):
        for repair_order in self.mapped("repair_order_ids"):
            repair_order.write(
                {
                    "state": "confirmed",
                }
            )

    def action_confirm(self):
        res = super().action_confirm()
        self._change_repair_order_status_done()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self._change_repair_order_status_confirmed()
        return res


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    repair_line_ids = fields.One2many(
        comodel_name="repair.line",
        inverse_name="sale_line_id",
        string="Repair lines",
        required=False,
    )
