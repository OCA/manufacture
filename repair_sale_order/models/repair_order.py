# Copyright 2022 ForgeFlow S.L. (https://forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import UserError


class RepairOrder(models.Model):

    _inherit = "repair.order"

    create_sale_order = fields.Boolean(related="repair_type_id.create_sale_order")
    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Sale orders",
        compute="_compute_sale_order",
    )
    sale_order_count = fields.Integer(
        string="Sale order count",
        compute="_compute_sale_order",
    )

    def _compute_sale_order(self):
        for rec in self:
            rec.sale_order_ids = rec.mapped("operations.sale_line_id.order_id").ids
            rec.sale_order_count = len(rec.sale_order_ids)

    def action_show_sales_order(self, new_orders=False):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations")
        form_view = [(self.env.ref("sale.view_order_form").id, "form")]
        orders = new_orders
        if not new_orders:
            orders = self.mapped("sale_order_ids")
        if len(orders) == 1:
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = orders.ids[0]
        else:
            action["domain"] = [("id", "in", orders.ids)]
        return action

    def _get_sale_order_data(self):
        self.ensure_one()
        addresses = self.partner_id.address_get(["delivery"])
        self.address_id = addresses["delivery"]
        res = {
            "partner_id": self.partner_id.id,
            "partner_shipping_id": self.address_id.id,
            "origin": self.display_name,
            "note": self.quotation_notes,
        }
        return res

    def action_create_sale_order(self):
        order_model = self.env["sale.order"].sudo()
        order_line_model = self.env["sale.order.line"].sudo()
        orders = order_model.browse()
        for rec in self.filtered(
            lambda x: not x.sale_order_ids and x.create_sale_order
        ):
            sale_order_data = rec._get_sale_order_data()
            sale_order = order_model.create(sale_order_data)
            orders |= sale_order
            self.onchange_partner_id()
            for line in rec.operations:
                sale_order_line = order_line_model.create(
                    line._get_sale_line_data(sale_order)
                )
                line.sale_line_id = sale_order_line.id
        return self.action_show_sales_order(orders)

    def action_validate(self):
        if self.filtered(lambda x: x.create_sale_order and not x.operations):
            raise UserError(
                _(
                    "You should input at least one part line to"
                    " continue on create Sales Order from Repair Order"
                )
            )
        return super().action_validate()


class RepairLine(models.Model):

    _inherit = "repair.line"

    def _get_sale_line_data(self, sale_order):
        self.ensure_one()
        res = {
            "product_id": self.product_id.id,
            "name": self.name,
            "product_uom_qty": self.product_uom_qty,
            "price_unit": self.price_unit,
            "tax_id": self.tax_id and [(6, 0, self.tax_id.ids)] or [],
            "order_id": sale_order.id,
        }
        return res

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line", string="Sale line", copy=False
    )
