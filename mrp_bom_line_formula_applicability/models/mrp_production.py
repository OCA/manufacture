#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def _compute_move_raw_ids(self):
        res = super()._compute_move_raw_ids()
        for production in self:
            moves_to_remove = self.env["stock.move"]
            for move in production.move_raw_ids:
                if move.bom_line_id and move.bom_line_id.applicability_formula:
                    applicability = move.bom_line_id._eval_applicability_formula(
                        move.product_id,
                        move.product_uom,
                        move.product_uom_qty,
                        production,
                        operation_id=move.operation_id,
                    )
                    if not applicability:
                        moves_to_remove |= move
            production.move_raw_ids -= moves_to_remove
        return res
