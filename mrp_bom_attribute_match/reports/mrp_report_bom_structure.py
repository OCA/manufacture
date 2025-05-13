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
        parent_product=False,
        index=0,
        product_info=False,
        ignore_stock=False,
        simulated_leaves_per_workcenter=False,
    ):
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
        data = super()._get_bom_data(
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
        # Replace any NewId value by the real record id
        # Otherwise it's evaluated as False in some situations, and it may cause issues
        if has_template_lines:
            for component in data.get("components", []):
                for key, value in component.items():
                    if isinstance(value, models.NewId):
                        component[key] = value.origin
        return data
