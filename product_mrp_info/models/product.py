# Copyright 2019 ForgeFlow S.L.
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_count = fields.Integer(
        string="# Manufacturing Orders",
        compute="_compute_mo_count",
    )

    def _compute_mo_count(self):
        read_group_res = self.env["mrp.production"]._read_group(
            [("product_id", "in", self.product_variant_ids.ids)],
            ["product_id"],
            ["__count"],
        )
        mapped_data = dict(read_group_res)
        for template in self:
            count = 0
            for variant in template.product_variant_ids:
                count += mapped_data.get(variant, 0)
            template.mo_count = count

    def action_view_mrp_productions(self):
        product_ids = self.product_variant_ids.ids
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.act_product_mrp_production_workcenter"
        )
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
        read_group_res = self.env["mrp.production"]._read_group(
            [("product_id", "in", self.ids)], ["product_id"], ["__count"]
        )
        mapped_data = dict(read_group_res)
        for product in self:
            product.mo_count = mapped_data.get(product, 0)

    def action_view_mrp_productions(self):
        product_ids = self.ids
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.act_product_mrp_production_workcenter"
        )
        action["domain"] = [("product_id", "in", product_ids)]
        action["context"] = {}
        return action
