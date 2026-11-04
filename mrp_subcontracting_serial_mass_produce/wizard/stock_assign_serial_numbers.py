# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockAssignSerialNumbers(models.TransientModel):
    _inherit = "stock.assign.serial"

    def _assign_serial_numbers(self, cancel_remaining_quantity=False):
        res = super()._assign_serial_numbers(cancel_remaining_quantity)
        if (
            not self.production_id._get_subcontract_move()
            or self.production_id.product_id.tracking != "serial"
        ):
            return res
        serial_numbers = set(self._get_serial_numbers())
        if not serial_numbers:
            return res
        assigned_lots = self.env["stock.lot"].search(
            [
                ("name", "in", list(serial_numbers)),
                ("product_id", "=", self.production_id.product_id.id),
            ]
        )
        productions = (
            self.production_id.procurement_group_id.mrp_production_ids.filtered(
                lambda mo: mo.state not in ("done", "cancel")
                and not mo.subcontracting_has_been_recorded
                and mo._get_subcontract_move()
                and mo.lot_producing_id
                and mo.lot_producing_id in assigned_lots
            )
        )
        for production in productions:
            # Skip consumption warning since qty is set by _split_productions
            production.with_context(
                cancel_backorder=False, skip_consumption=True
            ).subcontracting_record_component()
        return res
