# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_bom_price(self, bom, boms_to_recompute=False, byproduct_bom=False):
        # OVERRIDE to fill in the `line.product_id` if a component template is used.
        # To avoid a complete override, we HACK the bom by replacing it with a virtual
        # record, and modifying it's lines on-the-fly.
        has_template_lines = bom and any(
            line.component_template_id for line in bom.bom_line_ids
        )
        if has_template_lines:
            bom = bom.new(origin=bom)
            to_ignore_line_ids = []
            for line in bom.bom_line_ids:
                if line._skip_bom_line(self) or not line.component_template_id:
                    continue
                line_product = bom._get_component_template_product(
                    line, self, line.product_id
                )
                if not line_product:
                    to_ignore_line_ids.append(line.id)
                    continue
                else:
                    line.product_id = line_product
            if to_ignore_line_ids:
                bom.bom_line_ids = [Command.unlink(id) for id in to_ignore_line_ids]
        return super()._compute_bom_price(bom, boms_to_recompute, byproduct_bom)
