# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        parent_product=False,
        index=0,
        product_info=False,
        ignore_stock=False,
        simulated_leaves_per_workcenter=False,
    ):
        res = super()._get_bom_data(
            bom,
            warehouse,
            product=product,
            line_qty=line_qty,
            bom_line=bom_line,
            level=level,
            parent_bom=parent_bom,
            parent_product=parent_product,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
            simulated_leaves_per_workcenter=simulated_leaves_per_workcenter,
        )
        line_ids = bom.bom_line_ids
        for line in res["components"]:
            bom_line = line_ids.filtered(
                lambda x, line=line: x.location_id
                and x.product_id.id == line["product_id"]
            )
            line["location_id"] = bom_line.location_id or ""
        if parent_bom and parent_bom.location_id.complete_name:
            res["location"] = parent_bom.location_id.complete_name
        else:
            res["location"] = bom.location_id.complete_name or ""
        return res

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        product,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        res = super()._get_component_data(
            parent_bom,
            product,
            warehouse,
            bom_line,
            line_quantity,
            level,
            index,
            product_info,
            ignore_stock=ignore_stock,
        )
        # line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", parent_bom.id)])
        res["location"] = parent_bom.location_id.complete_name or ""
        return res

    @api.model
    def _get_pdf_line(
        self, bom_id, product_id=False, qty=1, unfolded_ids=None, unfolded=False
    ):
        res = super()._get_pdf_line(bom_id, product_id, qty, unfolded_ids, unfolded)
        line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", bom_id)])
        for line in res["lines"]:
            line_id = line_ids.filtered(
                lambda x, line=line: x.location_id
                and x.product_id.display_name == line["name"]
            )
            line["location_name"] = line_id.location_id.complete_name or ""
        return res
