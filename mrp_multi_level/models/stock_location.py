# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import ast

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    mrp_area_count = fields.Integer(
        string="MRP Area Parameter Count",
        readonly=True,
        compute="_compute_mrp_area_count",
    )

    def _compute_mrp_area_count(self):
        for rec in self:
            areas = self.env["mrp.area"].search([("location_id", "=", rec.id)])
            rec.mrp_area_count = len(areas)

    def action_view_mrp_area_location(self):
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_multi_level.mrp_area_action"
        )
        ctx = ast.literal_eval(result.get("context"))
        if not ctx:
            ctx = {}
        mrp_areas = self.env["mrp.area"].search([("location_id", "=", self.id)])
        if self.mrp_area_count != 1:
            result["domain"] = [("id", "in", mrp_areas.ids)]
        else:
            ctx.update({"default_mrp_area_id": mrp_areas[0].id})
            res = self.env.ref("mrp_multi_level.mrp_area_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = mrp_areas[0].id
        result["context"] = ctx
        return result
