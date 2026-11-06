# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.tools import config


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _is_consumed_qty_sync_enabled(self):
        """The tests of other modules expect the Odoo core consumption, so the
        sync only applies in the tests that ask for it.
        """
        return not config["test_enable"] or self.env.context.get(
            "test_mrp_2_steps_consumed_qty_sync"
        )

    def _is_consumed_from_pick(self):
        """The component comes from a pick components picking, so its
        consumption is what has been picked, nothing until it is picked.
        """
        self.ensure_one()
        if not self._is_consumed_qty_sync_enabled():
            return False
        production = self.raw_material_production_id
        if not production:
            return False
        pick_type = production.picking_type_id.warehouse_id.pbm_type_id
        return any(sm.picking_type_id == pick_type for sm in self.move_orig_ids)

    def _get_pick_demand(self):
        """Quantities picked for the component plus the ones still pending to
        pick. When a production backorder is created, both productions share the
        done picks, so the quantities taken from them by the other productions
        are not counted.
        """
        self.ensure_one()
        demand = sum(
            sm.quantity if sm.state == "done" else sm.product_uom_qty
            for sm in self.move_orig_ids
            if sm.state != "cancel"
        )
        done_picks = self.move_orig_ids.filtered(lambda sm: sm.state == "done")
        siblings = (done_picks.move_dest_ids - self).filtered(
            lambda sm: sm.state != "cancel"
        )
        return max(demand - sum(siblings.mapped("quantity")), 0.0)

    def _should_bypass_set_qty_producing(self):
        """Setting the quantity to produce (starting a work order, editing it or
        the produced lot in the form) must neither consume components pending to
        pick nor change the picked quantities.
        """
        if self._is_consumed_from_pick():
            return True
        return super()._should_bypass_set_qty_producing()
