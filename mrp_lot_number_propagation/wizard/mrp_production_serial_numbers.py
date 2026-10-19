# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from collections import deque

from odoo import api, exceptions, fields, models


class MrpBatchProduct(models.TransientModel):
    _inherit = "mrp.production.serials"

    is_lot_number_propagated = fields.Boolean(
        related="production_id.is_lot_number_propagated"
    )
    lot_number_propagation_alert_msg = fields.Char(
        compute="_compute_lot_number_propagation_alert_msg"
    )

    @api.depends("is_lot_number_propagated")
    def _compute_lot_number_propagation_alert_msg(self):
        for wiz in self:
            msg = ""
            if wiz.is_lot_number_propagated:
                propagated_component = (
                    wiz.production_id._get_propagating_component_move().product_id
                )
                msg = self.env._(
                    "Lot number must be the same between finished product %(product)s "
                    "and component %(component)s",
                    product=wiz.production_id.product_id.display_name,
                    component=propagated_component.display_name,
                )
            wiz.lot_number_propagation_alert_msg = msg

    def action_apply(self):
        self._check_propagated_lot_number()
        self = self.with_context(lot_propagation=True)
        return super().action_apply()

    def _check_propagated_lot_number(self):
        if not self.is_lot_number_propagated:
            return
        # Use deque to mimic what is done in MrpBatchProduct_production_text_to_object
        for production_line in deque(self.serial_numbers.split("\n")):
            production_line = production_line.strip()
            components_line = deque(production_line.split(self.component_separator))
            finished_line = components_line.popleft()
            for i, move_raw in enumerate(self.production_id.move_raw_ids):
                if move_raw.product_id.tracking == "none":
                    continue
                if (
                    move_raw.propagate_lot_number
                    and components_line[i] != finished_line
                ):
                    raise exceptions.UserError(
                        self.env._(
                            "As the product being produced is set to propagate lot "
                            "number from component %s, please make sure you define "
                            "the same lot number between finished product and "
                            "propagating component.",
                            self.production_id._get_propagating_component_move().product_id.display_name,
                        )
                    )
