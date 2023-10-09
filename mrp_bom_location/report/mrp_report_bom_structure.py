# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_pdf_doc(self, bom_id, data, quantity, product_variant_id=None):
        doc = super()._get_pdf_doc(bom_id, data, quantity, product_variant_id)
        doc["show_location"] = (
            True if data and data.get("show_location") == "true" else False
        )
        return doc

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
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        res = super(BomStructureReport, self)._get_bom_data(
            bom,
            warehouse,
            product=product,
            line_qty=line_qty,
            bom_line=bom_line,
            level=level,
            parent_bom=parent_bom,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
        )
        if parent_bom and parent_bom.location_id.complete_name:
            res["location"] = parent_bom.location_id.complete_name
        else:
            res["location"] = bom.location_id.complete_name or ""
        return res

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        res = super(BomStructureReport, self)._get_component_data(
            parent_bom,
            warehouse,
            bom_line,
            line_quantity,
            level,
            index,
            product_info,
            ignore_stock=ignore_stock,
        )
        res["location"] = parent_bom.location_id.complete_name or ""
        return res

    def _get_bom_array_lines(
        self, data, level, unfolded_ids, unfolded, parent_unfolded
    ):
        lines = super()._get_bom_array_lines(
            data, level, unfolded_ids, unfolded, parent_unfolded
        )
        for component in data.get("components", []):
            if not component["bom_id"]:
                continue
            bom_line = next(
                filter(lambda l: l.get("bom_id", None) == component["bom_id"], lines)
            )
            if bom_line:
                bom_line["location"] = component["location"]
        return lines
