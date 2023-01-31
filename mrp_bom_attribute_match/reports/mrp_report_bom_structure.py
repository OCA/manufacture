# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        # OVERRIDE to fill in the `line.product_id` if a component template is used.
        # To avoid a complete override, we HACK the bom by replacing it with a virtual
        # record, and modifying it's lines on-the-fly.
        has_template_lines = any(
            line.component_template_id for line in bom.bom_line_ids
        )
        if has_template_lines:
            bom = bom.new(origin=bom)
            to_ignore_line_ids = []
            for line in bom.bom_line_ids:
                if line._skip_bom_line(product) or not line.component_template_id:
                    continue
                line_product = bom._get_component_template_product(
                    line, product, line.product_id
                )
                if not line_product:
                    to_ignore_line_ids.append(line.id)
                    continue
                else:
                    line.product_id = line_product
            if to_ignore_line_ids:
                bom.bom_line_ids = [Command.unlink(id) for id in to_ignore_line_ids]
        components, total = super()._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        # Replace any NewId value by the real record id
        # Otherwise it's evaluated as False in some situations, and it may cause issues
        if has_template_lines:
            for component in components:
                for key, value in component.items():
                    if isinstance(value, models.NewId):
                        component[key] = value.origin
        return components, total
