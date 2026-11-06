# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import Command, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _set_quantity_done_prepare_vals(self, qty):
        res = super()._set_quantity_done_prepare_vals(qty)
        if not (self.raw_material_production_id or self.production_id):
            return res
        for command in res:
            if command[0] != Command.CREATE:
                continue
            vals = command[2]
            if (
                vals.get("picked")
                and vals.get("quantity")
                and not vals.get("qty_picked")
            ):
                vals["qty_picked"] = vals["quantity"]
        return res
