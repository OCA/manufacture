# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_finish(self):
        """Finishing a work order consumes its components in proportion to the
        quantity produced. The components that come from the pick keep what has
        been picked instead, so nothing is consumed for the pending ones.
        """
        pick_moves = self.move_raw_ids.filtered(
            lambda sm: sm.state not in ("done", "cancel")
            and not sm.picked
            and sm._is_consumed_from_pick()
        )
        res = super().button_finish()
        pick_moves = pick_moves.filtered("picked")
        pick_moves.picked = False
        pick_moves._do_unreserve()
        pick_moves._action_assign()
        return res
