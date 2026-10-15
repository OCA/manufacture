# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import float_compare, float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _generate_backorder_productions(self, close_mo=True):
        """When a backorder is created, the production keeps the part of the
        picked quantities proportional to the quantity produced, as Odoo core
        does, but never more than what has been picked. The rest stays reserved
        for the backorder.
        """
        for production in self:
            for move in production.move_raw_ids.filtered(
                lambda sm: sm.state not in ("done", "cancel")
                and sm._is_consumed_from_pick()
            ):
                rounding = move.product_uom.rounding
                qty = float_round(
                    move.unit_factor * production.qty_producing,
                    precision_rounding=rounding,
                )
                if (
                    float_compare(move.quantity_done, qty, precision_rounding=rounding)
                    > 0
                ):
                    move.move_line_ids.filtered(
                        lambda ml: ml.state not in ("done", "cancel")
                    ).qty_done = 0
                    move._set_quantity_done(qty)
        return super()._generate_backorder_productions(close_mo=close_mo)

    def button_mark_done(self):
        """Backorders consume what is reserved for them from the picked
        quantities, as when a pick components picking is validated.
        """
        groups = self.procurement_group_id
        previous = groups.mrp_production_ids
        res = super().button_mark_done()
        backorders = groups.mrp_production_ids - previous
        moves = backorders.move_raw_ids.filtered(
            lambda sm: sm.state not in ("done", "cancel")
            and sm._is_consumed_from_pick()
        )
        moves._action_assign()
        moves._set_quantities_to_reservation()
        return res
