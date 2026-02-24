# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# Copyright 2026 CHEF PIXEL
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_report_data(self, bom_id, **kwargs):
        res = super()._get_report_data(bom_id, **kwargs)

        if isinstance(res, dict):
            components = res.get("components", [])
            if any(
                isinstance(c, dict) and c.get("is_variant_applied") for c in components
            ):
                res["is_variant_applied"] = True
        return res

    @api.model
    def _get_bom_data(self, bom, warehouse, product=False, **kwargs):
        variant_matched = False

        # Only process if a product is given and BOM has component templates
        if product and any(line.component_template_id for line in bom.bom_line_ids):
            # Create a new BOM record to avoid modifying original
            bom = bom.new(origin=bom)

            for line in bom.bom_line_ids:
                if not line.component_template_id:
                    continue
                # Match component template to actual product
                matched_product = bom._get_component_template_product(
                    line, product, line.product_id
                )
                if matched_product:
                    line.product_id = matched_product
                    variant_matched = True

        # Get BOM data from parent
        data = super()._get_bom_data(bom, warehouse, product=product, **kwargs)

        if variant_matched:
            data["is_variant_applied"] = True

        components = data.get("components", [])
        for component in components:
            if not isinstance(component, dict):
                continue

            if component.get("is_variant_applied"):
                data["is_variant_applied"] = True

            for key, value in component.items():
                if hasattr(value, "origin"):
                    component[key] = value.origin

        return data
