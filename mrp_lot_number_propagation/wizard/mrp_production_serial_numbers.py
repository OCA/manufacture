# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import UserError


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
                    "Lot numbers from the component %(component)s are propagated to "
                    "the finished product %(product)s",
                    product=wiz.production_id.product_id.display_name,
                    component=propagated_component.display_name,
                )
            wiz.lot_number_propagation_alert_msg = msg

    @api.depends("production_id")
    def _compute_lot_name(self):  # pylint: disable=missing-return
        # In-place compute: we must run the core computation first, then
        #  adjust the results, so we cannot return the super() call.
        super()._compute_lot_name()
        for wiz in self:
            if not wiz.is_lot_number_propagated or wiz.serial_numbers:
                continue
            # Prefill the serial numbers with the ones reserved on the
            # propagating component, so the user only has to confirm them.
            propagated_names = wiz.production_id._get_propagated_lot_names()
            if propagated_names:
                wiz.serial_numbers = "\n".join(propagated_names)
                wiz.lot_name = propagated_names[0]

    def action_apply(self):
        self._check_propagated_lot_number()
        self = self.with_context(lot_propagation=True)
        return super().action_apply()

    def action_split_and_assign_serials(self):
        self._check_propagated_lot_number()
        self = self.with_context(lot_propagation=True)
        return super().action_split_and_assign_serials()

    def _check_propagated_lot_number(self):
        if not self.is_lot_number_propagated:
            return
        # The wizard holds one finished serial name per line.
        # The propagation rule is a 1:1 match by name between those serials
        # and the one reserved on the component.
        expected_names = self.production_id._get_propagated_lot_names()
        entered_names = [
            line.strip()
            for line in (self.serial_numbers or "").split("\n")
            if line.strip()
        ]
        if not expected_names:
            raise UserError(
                self.env._(
                    "Cannot propagate lot number: no serial number is reserved "
                    "on the propagating component. Please reserve it first."
                )
            )
        if sorted(entered_names) != sorted(expected_names):
            raise UserError(
                self.env._(
                    "As the product being produced is set to propagate lot "
                    "number from component %s, the finished product serial "
                    "numbers must be exactly the ones reserved on that "
                    "component.",
                    self.production_id._get_propagating_component_move().product_id.display_name,
                )
            )
