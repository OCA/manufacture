# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _cal_price(self, consumed_moves):
        # OVERRIDE to use the theoretical duration of the workcenter
        # This will overwrite the real duration of the workcenter, but that's ok for now
        should_overwrite_duration = (
            self.product_id.mrp_workcenter_cost == "theoretical"
            and not any(t.cost_already_recorded for t in self.workorder_ids.time_ids)
        )
        duration_by_workorder = {}
        if should_overwrite_duration:
            workorders = self.workorder_ids.filtered("duration_expected")
            for workorder in workorders:
                duration_by_workorder[workorder.id] = workorder.duration
                workorder.duration = workorder.duration_expected
        res = super()._cal_price(consumed_moves)
        # Restore the durations set by users
        if should_overwrite_duration:
            for workorder in workorders:
                workorder.duration = duration_by_workorder[workorder.id]
        return res
