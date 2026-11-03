# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    propagate_lot_number = fields.Boolean(
        default=False,
        readonly=True,
    )

    def _action_assign(self, force_qty=False):
        res = super()._action_assign(force_qty=force_qty)
        self._ensure_production_propagating_finished_lot()
        return res

    def _ensure_production_propagating_finished_lot(self):
        # In case a lot propagating component is scrapped or unreserved after MOs were
        #  split through the mass produce wizard, the finished lot will still match
        #  the removed propagating component, so we must remove the outdated finished
        #  lot
        for move in self:
            order = move.raw_material_production_id
            finished_lots = order.lot_producing_ids
            if not (move.propagate_lot_number and finished_lots):
                continue
            component_names = move.move_line_ids.filtered(lambda ln: ln.lot_id).mapped(
                "lot_id.name"
            )
            if sorted(component_names) == sorted(finished_lots.mapped("name")):
                continue
            order.write({"lot_producing_ids": False})
            for finished_lot in finished_lots:
                if not finished_lot.quant_ids:
                    finished_lot.unlink()
