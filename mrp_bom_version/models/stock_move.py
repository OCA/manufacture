# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _compute_kit_quantities(self, product_id, kit_qty, kit_bom, filters):
        if len(self.bom_line_id.bom_id) == 1 and self.bom_line_id.bom_id != kit_bom:
            if self.bom_line_id.bom_id.version < kit_bom.version:
                kit_bom = self.bom_line_id.bom_id
        return super()._compute_kit_quantities(product_id, kit_qty, kit_bom, filters)
