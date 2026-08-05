# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, models


class ReportBomStructure(models.AbstractModel):
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
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        # OVERRIDE to fill in the `line.product_id` if a component template is used.
        # To avoid a complete override, we HACK the bom by replacing it with a virtual
        # record, and modifying it's lines on-the-fly.
        component_template_ids = bom.bom_line_ids.component_template_id

        if component_template_ids:
            bom = bom.new(origin=bom)
            lines_to_ignore = []

            for line_id in bom.bom_line_ids:
                if line_id._skip_bom_line(product) or not line_id.component_template_id:
                    continue

                line_product_id = bom._get_component_or_product_id(
                    line_id, product, line_id.product_id
                )

                if not line_product_id:
                    lines_to_ignore.append(line_id.id)
                    continue

                else:
                    line_id.product_id = line_product_id

            if lines_to_ignore:
                bom.bom_line_ids = [Command.unlink(line) for line in lines_to_ignore]

        data = super()._get_bom_data(
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

        # Replace any NewId value by the real record id
        # Otherwise it's evaluated as False in some situations, and it may cause issues
        if component_template_ids:
            for component in data.get("components", []):
                for key, value in component.items():
                    if isinstance(value, models.NewId):
                        component[key] = value.origin

        return data
