# Copyright 2026 apik (https://apik.cloud).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for record in self:
            productions = record.move_ids.move_orig_ids.production_id.filtered(
                lambda p: (
                    p.is_lot_number_propagated and p.state not in ("done", "cancel")
                )
            )

            for production in productions:
                sbc_moves = production._get_subcontract_move()
                if not sbc_moves:
                    continue

                lot_names = production._get_propagated_lot_names()
                if not lot_names:
                    continue

                lots = production._create_or_get_propagated_lots(lot_names)

                # Retrieve receipt move lines in a stable order.
                move_lines = sbc_moves.move_line_ids.sorted("id")

                if len(move_lines) != len(lots):
                    raise UserError(
                        self.env._(
                            "The number of receipt move lines does not "
                            "match the number of propagated lots for "
                            "MO %(name)s.",
                            name=production.name,
                        )
                    )

                # Assign lots without triggering subcontracting sync
                # on each individual move line.
                for move_line, lot in zip(move_lines, lots, strict=True):
                    move_line.with_context(
                        mrp_subcontracting=True,
                    ).write(
                        {
                            "lot_id": lot.id,
                        }
                    )
                # Run standard subcontracting synchronization once.
                sbc_moves.with_context(
                    no_procurement=True,
                    lot_propagation=True,
                )._sync_subcontracting_productions()

        return super().button_validate()
