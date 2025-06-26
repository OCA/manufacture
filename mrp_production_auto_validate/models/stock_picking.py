# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_manufacturing_orders(self, states=None):
        self.ensure_one()
        if states is None:
            states = ("confirmed", "progress")
        return self.move_ids.move_dest_ids.raw_material_production_id.filtered(
            lambda o: o.state in states
        )

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            if picking.state != "done":
                continue
            orders = picking._get_manufacturing_orders()
            if not orders:
                continue
            for order in orders:
                # NOTE: use of 'reservation_state' doesn't allow to produce
                # at least 1 finished product even if there is enough components,
                # but Odoo expects to work this way.
                if order.auto_validate and order.reservation_state == "assigned":
                    # 'stock.immediate.transfer' could set the 'skip_immediate'
                    # key to process the transfer. The same ctx key is used by
                    # MO validation methods, but they are not the same!
                    # Unset the key in such case.
                    # TODO add a test
                    if order.env.context.get("skip_immediate"):
                        order = order.with_context(skip_immediate=False)
                    order._auto_validate_after_picking()
        return res
