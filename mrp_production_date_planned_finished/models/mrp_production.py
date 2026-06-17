# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_date_start_using_delays(self):
        date_start = self.date_finished
        date_start -= relativedelta(days=self.bom_id.produce_delay)
        return date_start

    @api.onchange("date_finished")
    def _onchange_date_finished_set_date_start(self):
        if self.date_finished and not self.is_planned:
            date_start = self._get_date_start_using_delays()
            if date_start == self.date_finished:
                date_start -= relativedelta(hours=1)
            if self.date_start != date_start:
                self.date_start = date_start
                self.move_raw_ids = [
                    (1, m.id, {"date": self.date_start}) for m in self.move_raw_ids
                ]
