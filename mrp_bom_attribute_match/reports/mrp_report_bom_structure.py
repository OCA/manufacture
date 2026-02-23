# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# Copyright 2026 CHEF PIXEL
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_report_data(self, bom_id, *args, **kwargs):
        res = super()._get_report_data(bom_id, *args, **kwargs)
        if isinstance(res, dict):
            components = res.get("components", [])
            if any(
                c.get("is_variant_applied") for c in components if isinstance(c, dict)
            ):
                res["is_variant_applied"] = True
        return res

    @api.model
    def _get_bom_data(self, bom, warehouse, product=False, **kwargs):
        variant_matched = False
        if product:
            has_templates = any(line.component_template_id for line in bom.bom_line_ids)
            if has_templates:
                bom = bom.new(origin=bom)
                for line in bom.bom_line_ids:
                    if not line.component_template_id:
                        continue
                    line_product = bom._get_component_template_product(
                        line, product, line.product_id
                    )
                    if line_product:
                        line.product_id = line_product
                        variant_matched = True

        data = super()._get_bom_data(bom, warehouse, product=product, **kwargs)

        if variant_matched:
            data["is_variant_applied"] = True

        components = data.get("components", [])
        for component in components:
            if isinstance(component, dict):
                if component.get("is_variant_applied"):
                    data["is_variant_applied"] = True
                for key, value in component.items():
                    if hasattr(value, "origin"):
                        component[key] = value.origin
        return data
