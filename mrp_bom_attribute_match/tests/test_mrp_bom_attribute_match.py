# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_report_data(self, bom_id, search_qty=0, search_variant=False):
        """Matches the Odoo 19 base signature exactly to avoid TypeErrors."""
        res = super()._get_report_data(
            bom_id, search_qty=search_qty, search_variant=search_variant
        )

        if isinstance(res, dict):
            components = res.get("components", [])
            is_applied = any(
                c.get("is_variant_applied") for c in components if isinstance(c, dict)
            )
            if is_applied:
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
