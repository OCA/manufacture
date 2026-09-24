# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tools import float_round


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _get_duration_expected(self, alternative_workcenter=False, ratio=1):
        # Extend the expected duration with fixed time and cadence-based time.
        # On top of the standard time_cycle (minutes-per-unit * capacity),
        # two additional contributions from the BOM operation are applied:
        #   - time_fixed:   flat minutes added once per work order, independent
        #                   of the quantity to produce.
        #   - time_cadence: production rate in units/minute; contributes
        #                   qty / time_cadence minutes of working time.
        # Both extra contributions are subject to the workcenter efficiency
        # factor (same as the base time_cycle working time).
        duration = super()._get_duration_expected(
            alternative_workcenter=alternative_workcenter, ratio=ratio
        )

        operation = self.operation_id
        if not operation or (not operation.time_fixed and not operation.time_cadence):
            return duration

        workcenter = alternative_workcenter or self.workcenter_id
        if not workcenter:
            return duration

        efficiency = workcenter.time_efficiency or 100.0
        qty_production = self.production_id.product_uom_id._compute_quantity(
            self.qty_producing or self.qty_production,
            self.production_id.product_id.uom_id,
        )

        extra_working_time = 0.0

        if operation.time_fixed:
            extra_working_time += operation.time_fixed

        if operation.time_cadence > 0:
            capacity = workcenter._get_capacity(self.product_id)
            cycle_number = float_round(
                qty_production / capacity,
                precision_digits=0,
                rounding_method="UP",
            )
            extra_working_time += cycle_number * (capacity / operation.time_cadence)

        return duration + extra_working_time * 100.0 / efficiency
