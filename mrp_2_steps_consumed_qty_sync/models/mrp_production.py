# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_pick_moves_to_consume(self):
        return self.move_raw_ids.filtered(
            lambda sm: sm.state not in ("done", "cancel")
            and not sm.picked
            and sm.quantity
            and sm._is_consumed_from_pick()
        )

    def pre_button_mark_done(self):
        """The picked quantities are consumed, as Odoo core does with the
        components of manual consumption.
        """
        self._get_pick_moves_to_consume().picked = True
        return super().pre_button_mark_done()

    def _split_productions(
        self, amounts=False, cancel_remaining_qty=False, set_consumed_qty=False
    ):
        """When a backorder is created, the picked quantities are split in
        proportion to the quantity produced, as Odoo core does with components
        not consumed yet, never more than what has been picked.
        """
        self.move_raw_ids.filtered(
            lambda sm: sm.state not in ("done", "cancel")
            and sm.picked
            and sm._is_consumed_from_pick()
        ).picked = False
        return super()._split_productions(
            amounts=amounts,
            cancel_remaining_qty=cancel_remaining_qty,
            set_consumed_qty=set_consumed_qty,
        )

    def _post_inventory(self, cancel_backorder=False):
        """Each production consumes the picked quantities it holds, also after
        splitting them with a backorder.
        """
        self._get_pick_moves_to_consume().picked = True
        return super()._post_inventory(cancel_backorder=cancel_backorder)
