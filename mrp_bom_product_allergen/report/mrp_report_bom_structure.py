# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.image import image_data_uri


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        parent_product,
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
            parent_product,
            warehouse,
            bom_line,
            line_quantity,
            level,
            index,
            product_info,
            ignore_stock,
        )
        res.update(
            {
                "allergen_ids": bom_line.product_id.allergen_ids,
                "allergen_imgs": [
                    image_data_uri(allergen.image)
                    for allergen in bom_line.product_id.allergen_ids
                ],
            }
        )
        return res

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
        # Extend to add the allergen_ids field
        res = super()._get_bom_data(
            bom,
            warehouse,
            product,
            line_qty,
            bom_line,
            level,
            parent_bom,
            parent_product,
            index,
            product_info,
            ignore_stock,
            simulated_leaves_per_workcenter,
        )
        res["allergen_ids"] = self.env["allergen.allergen"]
        for component in res["components"]:
            res["allergen_ids"] |= component["allergen_ids"]
        res["allergen_imgs"] = [
            image_data_uri(allergen.image) for allergen in res["allergen_ids"]
        ]
        return res

    @api.model
    def _get_bom_array_lines(
        self, data, level, unfolded_ids, unfolded, parent_unfolded=True
    ):
        lines = super()._get_bom_array_lines(
            data, level, unfolded_ids, unfolded, parent_unfolded
        )
        for index, bom_line in enumerate(data["components"]):
            if lines[index]["type"] in ("bom", "component"):
                lines[index]["allergen_ids"] = bom_line["allergen_ids"]
                lines[index]["allergen_imgs"] = bom_line["allergen_imgs"]
        return lines
