# Copyright 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import ast

from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    llc = fields.Integer(related="mrp_product_llc_id.llc")
    mrp_product_llc_id = fields.Many2one(comodel_name="mrp.product.llc")
    manufacturing_order_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="product_id",
        string="Manufacturing Orders",
        domain=[("state", "=", "draft")],
    )
    purchase_order_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        string="Purchase Orders",
    )
    mrp_area_ids = fields.One2many(
        comodel_name="product.mrp.area",
        inverse_name="product_id",
        string="MRP Area parameters",
    )
    mrp_area_count = fields.Integer(
        string="MRP Area Parameter Count",
        readonly=True,
        compute="_compute_mrp_area_count",
    )

    def _compute_mrp_area_count(self):
        for rec in self:
            rec.mrp_area_count = len(rec.mrp_area_ids)

    def write(self, values):
        res = super().write(values)
        if values.get("active") is False:
            parameters = (
                self.env["product.mrp.area"]
                .sudo()
                .search([("product_id", "in", self.ids)])
            )
            parameters.write({"active": False})
        if not values.get("mrp_product_llc_id", True):
            mrp_product_llc = self.env["mrp.product.llc"].create(
                {
                    "product_id": self.id,
                    "llc": 0
                }
            )
            values.update({"mrp_product_llc_id": mrp_product_llc.id})
        return res

    def action_view_mrp_area_parameters(self):
        self.ensure_one()
        action = self.env.ref("mrp_multi_level.product_mrp_area_action")
        result = action.read()[0]
        ctx = ast.literal_eval(result.get("context"))
        if not ctx:
            ctx = {}
        mrp_areas = self.env["mrp.area"].search([])
        if len(mrp_areas) == 1:
            ctx.update({"default_mrp_area_id": mrp_areas[0].id})
        area_ids = self.mrp_area_ids.ids
        ctx.update({"default_product_id": self.id})
        if self.mrp_area_count != 1:
            result["domain"] = [("id", "in", area_ids)]
        else:
            res = self.env.ref("mrp_multi_level.product_mrp_area_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = area_ids[0]
        result["context"] = ctx
        return result
