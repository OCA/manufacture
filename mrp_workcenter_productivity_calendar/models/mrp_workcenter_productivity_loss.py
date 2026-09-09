# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpWorkcenterProductivityLoss(models.Model):
    _inherit = "mrp.workcenter.productivity.loss"

    def _convert_to_duration(self, date_start, date_stop, workcenter=False):
        use_calendar = (
            workcenter
            and workcenter.resource_calendar_id
            and workcenter.use_calendar_for_duration
        )
        calendar_records = (
            self.filtered(lambda p: p.loss_type in ("productive", "performance"))
            if use_calendar
            else self.browse()
        )
        other_records = self - calendar_records

        duration = 0
        if calendar_records:
            # Reuse the same helper core uses for non-productive types below,
            # instead of resource_calendar_id.get_work_hours_count(), so
            # productive/performance time is deducted identically (same
            # naive-datetime-as-UTC handling, same resource-specific leaves).
            hours = workcenter._get_work_days_data_batch(date_start, date_stop)[
                workcenter.id
            ]["hours"]
            duration = hours * 60

        if other_records:
            res = super(
                MrpWorkcenterProductivityLoss, other_records
            )._convert_to_duration(date_start, date_stop, workcenter=workcenter)
            duration = max(duration, res)

        return round(duration, 2)
