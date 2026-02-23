# Copyright 2026 CHEF PIXEL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        bom_lines_to_reset = []
        for bom_line in self.bom_id.bom_line_ids:
            if bom_line.component_template_id and not bom_line.product_id:
                component_product = self.bom_id._get_component_template_product(
                    bom_line, self.product_id, bom_line.product_id
                )
                if component_product:
                    bom_line.product_id = component_product
                    bom_lines_to_reset.append(bom_line)
        res = super().action_confirm()
        for bom_line in bom_lines_to_reset:
            bom_line.product_id = False
        return res

    @api.constrains("bom_id")
    def _check_component_attributes(self):
        self.bom_id._check_component_attributes()
