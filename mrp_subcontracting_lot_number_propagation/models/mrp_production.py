# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        # New field dependencies to compute the propagated lot on the
        # "mrp_production_subcontracting_form_view" view.
        "move_raw_ids.move_line_ids.quantity",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        return super()._compute_propagated_lot_producing()

    def _sync_subcontract_move_lot_to_production(self):
        """Propagate receipt move lots to the subcontracted MO."""
        for order in self:
            sbc_move = order._get_subcontract_move()
            if not (order.is_lot_number_propagated and sbc_move):
                continue

            lots = sbc_move.move_line_ids.filtered(lambda ml: ml.lot_id).mapped(
                "lot_id"
            )

            if lots:
                order.with_context(lot_propagation=True).write(
                    {
                        "lot_producing_ids": [(6, 0, lots.ids)],
                    }
                )
