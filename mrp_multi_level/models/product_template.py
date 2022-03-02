# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import ast

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_area_ids = fields.One2many(
        comodel_name="product.mrp.area",
        inverse_name="product_tmpl_id",
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

    def action_view_mrp_area_parameters(self):
        self.ensure_one()
        xmlid = "mrp_multi_level.product_mrp_area_action"
        result = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        ctx = ast.literal_eval(result.get("context"))
        mrp_areas = self.env["mrp.area"].search([])
        if "context" not in result:
            result["context"] = {}
        if len(mrp_areas) == 1:
            ctx.update({"default_mrp_area_id": mrp_areas[0].id})
        mrp_area_ids = self.with_context(active_test=False).mrp_area_ids.ids
        if len(self.product_variant_ids) == 1:
            variant = self.product_variant_ids[0]
            ctx.update({"default_product_id": variant.id})
        if len(mrp_area_ids) != 1:
            result["domain"] = [("id", "in", mrp_area_ids)]
        else:
            res = self.env.ref("mrp_multi_level.product_mrp_area_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = mrp_area_ids[0]
        result["context"] = ctx
        return result
