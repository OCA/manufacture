# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for val in vals_list:
            if (
                self.env.context.get("group_mo_by_product", False)
                and "raw_material_production_id" in val
            ):
                mo = self.env["mrp.production"].browse(
                    val["raw_material_production_id"]
                )
                # MO already has raw materials
                if mo.move_raw_ids:
                    continue
                else:
                    new_vals_list.append(val)
            else:
                new_vals_list.append(val)
        return super(StockMove, self).create(new_vals_list)
