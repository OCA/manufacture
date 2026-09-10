# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# Copyright 2026 CHEF PIXEL
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_report_data(self, *args, **kwargs):
        """
        Retrieves BOM report data with variant information.
        Compatible with Odoo 19 / OCA signature.
        """
        res = super()._get_report_data(*args, **kwargs)

        if isinstance(res, dict):
            components = res.get("components", [])
            # If any component has variant applied, mark it
            if any(
                c.get("is_variant_applied") for c in components if isinstance(c, dict)
            ):
                res["is_variant_applied"] = any(
                    c.get("is_variant_applied")
                    for c in components
                    if isinstance(c, dict)
                )
        return res

    @api.model
    def _get_bom_data(self, bom, warehouse, product=False, **kwargs):
        """
        Returns BOM data, applying component template variants if needed.
        """
        variant_matched = False

        if product:
            has_templates = any(line.component_template_id for line in bom.bom_line_ids)
            if has_templates:
                # Create a safe copy of BOM to modify
                bom = bom.new(origin=bom)
                for line in bom.bom_line_ids:
                    line_product = bom._get_component_template_product(
                        line,
                        product,
                        line.product_id,
                    )
                    if line_product:
                        line.product_id = line_product
                        variant_matched = True

        data = super()._get_bom_data(bom, warehouse, product=product, **kwargs)

        if variant_matched:
            data["is_variant_applied"] = True

        # Ensure any component record objects are serialized properly
        components = data.get("components", [])
        for component in components:
            if component.get("is_variant_applied"):
                data["is_variant_applied"] = variant_matched or any(
                    c.get("is_variant_applied")
                    for c in components
                    if isinstance(c, dict)
                )
            for key, value in component.items():
                if hasattr(value, "origin"):
                    component[key] = value.origin

        return data
