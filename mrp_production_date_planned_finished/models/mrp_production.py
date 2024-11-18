# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_date_planned_start_using_delays(self):
        date_planned_start = self.date_planned_finished
        date_planned_start -= relativedelta(days=self.product_id.produce_delay)
        date_planned_start -= relativedelta(days=self.company_id.manufacturing_lead)
        return date_planned_start

    @api.onchange("date_planned_finished")
    def _onchange_date_planned_finished_set_date_planned_start(self):
        if self.date_planned_finished and not self.is_planned:
            date_planned_start = self._get_date_planned_start_using_delays()
            if date_planned_start == self.date_planned_finished:
                date_planned_start -= relativedelta(hours=1)
            if self.date_planned_start != date_planned_start:
                self.date_planned_start = date_planned_start
                self.move_raw_ids = [
                    (1, m.id, {"date": self.date_planned_start})
                    for m in self.move_raw_ids
                ]
