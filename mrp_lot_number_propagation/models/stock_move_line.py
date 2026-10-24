# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        self._check_propagating_finished_lot(lines.move_id)
        return lines

    def write(self, vals):
        res = super().write(vals)
        if "lot_id" not in vals:
            return res
        self._check_propagating_finished_lot(self.move_id)
        return res

    @staticmethod
    def _check_propagating_finished_lot(moves):
        moves = moves.exists().filtered(
            lambda move: move.propagate_lot_number
            and move.raw_material_production_id.exists()
            and move.raw_material_production_id.lot_producing_ids
        )
        moves._ensure_production_propagating_finished_lot()
