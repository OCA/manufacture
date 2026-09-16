# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    @api.onchange("date_start")
    def _date_start_changed(self):
        if not self.date_start:
            return
        if not self.workcenter_id.use_calendar_for_duration:
            self.date_end = self.date_start + timedelta(minutes=self.duration)
        self._loss_type_change()

    @api.onchange("date_end")
    def _date_end_changed(self):
        if not self.date_end:
            return
        if not self.workcenter_id.use_calendar_for_duration:
            self.date_start = self.date_end - timedelta(minutes=self.duration)
        self._loss_type_change()

    @api.onchange("duration")
    def _duration_changed(self):
        if not self.date_end:
            return
        if not self.workcenter_id.use_calendar_for_duration:
            self.date_start = self.date_end - timedelta(minutes=self.duration)
        self._loss_type_change()
