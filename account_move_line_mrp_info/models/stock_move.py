# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_account_move_line_vals(self):
        vals_list = super()._get_account_move_line_vals()
        production = self.production_id or self.raw_material_production_id
        for vals in vals_list:
            vals.update(
                {
                    "mrp_production_id": production.id,
                    "unbuild_id": self.unbuild_id.id,
                }
            )
        return vals_list
