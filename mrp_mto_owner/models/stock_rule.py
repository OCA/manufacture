# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        bom,
    ):
        vals = super(StockRule, self)._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        move_dest_ids = values.get("move_dest_ids")
        if move_dest_ids:
            origin_move = self._find_origin_move(move_dest_ids[0])
            if origin_move and origin_move.raw_material_production_id.owner_id:
                vals["owner_id"] = origin_move.raw_material_production_id.owner_id.id
        return vals

    def _find_origin_move(self, move):
        # Recursively find the very first (origin) move using move_dest_ids
        if move.move_dest_ids:
            return self._find_origin_move(move.move_dest_ids[0])
        else:
            return move
