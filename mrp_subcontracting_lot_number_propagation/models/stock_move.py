# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends(
        "move_line_ids.is_lot_id_editable",
    )
    def _compute_display_assign_serial(self):
        # Display (or not) the fields/buttons to assign/unassign serial numbers
        # depending on the 'is_lot_id_editable' field.
        # If one of the move line doesn't allow to edit the lot, we don't display
        # the fields/buttons at the move level.
        res = super()._compute_display_assign_serial()
        for move in self:
            all_lot_editable = all(move.move_line_ids.mapped("is_lot_id_editable"))
            if not all_lot_editable:
                move.display_assign_serial = False
        return res
