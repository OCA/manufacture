#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        initial_moves = super()._get_moves_raw_values()
        final_moves = []
        for move in initial_moves:
            if move.get("bom_line_id"):
                bom_line = self.env["mrp.bom.line"].browse(move["bom_line_id"])
                if bom_line.applicability_formula:
                    applicability = bom_line._eval_applicability_formula(
                        move["product_id"],
                        move["product_uom"],
                        move["product_uom_qty"],
                        self,
                        operation_id=move.get("operation_id"),
                    )
                    if not applicability:
                        continue
            final_moves.append(move)
        return final_moves
