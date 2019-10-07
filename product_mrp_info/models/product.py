# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# - Lois Rilo Antelo <lois.rilo@eficent.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_count = fields.Integer(
        string="# Manufacturing Orders",
        compute="_compute_mo_count",
    )

    @api.multi
    def _compute_mo_count(self):
        read_group_res = self.env["mrp.production"].read_group(
            [("product_id", "in", self.mapped("product_variant_ids").ids)],
            ["product_id"], ["product_id"])
        mapped_data = dict(
            [(data["product_id"][0], data["product_id_count"]) for data in
             read_group_res])
        for rec in self:
            count = 0
            for variant in rec.mapped("product_variant_ids"):
                count += mapped_data.get(variant.id, 0)
            rec.mo_count = count

    def action_view_mrp_productions(self):
        product_ids = self.mapped("product_variant_ids").ids
        action = self.env.ref("mrp.act_product_mrp_production").read()[0]
        action["domain"] = [("product_id", "in", product_ids)]
        action["context"] = {}
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    mo_count = fields.Integer(
        string="# Manufacturing Orders",
        compute="_compute_mo_count",
    )

    def _compute_mo_count(self):
        read_group_res = self.env["mrp.production"].read_group(
            [("product_id", "in", self.ids)], ["product_id"], ["product_id"])
        mapped_data = dict(
            [(data["product_id"][0], data["product_id_count"]) for data in
             read_group_res])
        for product in self:
            product.mo_count = mapped_data.get(product.id, 0)

    @api.multi
    def action_view_mrp_productions(self):
        product_ids = self.ids
        action = self.env.ref("mrp.act_product_mrp_production").read()[0]
        action["domain"] = [("product_id", "in", product_ids)]
        action["context"] = {}
        return action
