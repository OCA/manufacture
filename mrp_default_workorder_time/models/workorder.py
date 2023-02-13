# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MrpWorkOrder(models.Model):

    _inherit = "mrp.workorder"

    def add_time_to_work_order(self, fully_productive_time):
        self.ensure_one()
        # self._compute_duration()
        date_start = self.date_planned_start
        if not date_start:
            raise UserError(
                _(
                    "You should plan orders to set default "
                    "production time on work orders, please check"
                )
            )
        date_end = self.date_planned_start + relativedelta(
            minutes=self.duration_expected
        )
        if self.time_ids:
            minutes_to_add = self.duration_expected - self.duration
            if float_compare(minutes_to_add, 0, precision_digits=6) == -1:
                return
            date_start = max(self.time_ids.mapped("date_end"))
            date_end = date_start + relativedelta(minutes=minutes_to_add)
        self.write(
            {
                "time_ids": [
                    (
                        0,
                        0,
                        {
                            "user_id": self.env.user.id,
                            "date_start": date_start,
                            "date_end": date_end,
                            "loss_id": fully_productive_time.id,
                            "workcenter_id": self.workcenter_id.id,
                            "description": fully_productive_time.name,
                        },
                    )
                ]
            }
        )

    def reduce_time_to_workorder(self, fully_productive_time):
        self.ensure_one()
        self.time_ids.filtered(
            lambda x: x.loss_id.id == fully_productive_time.id
        ).sudo().unlink()
        self.add_time_to_work_order(fully_productive_time)

    def button_finish(self):
        res = super().button_finish()
        fully_productive_time = self.env["mrp.workcenter.productivity.loss"].search(
            [("loss_type", "=", "performance")], limit=1
        )
        if not fully_productive_time:
            raise UserError(
                _(
                    "Fully Productive Time is not configured on system, "
                    "please contact with your administrator"
                )
            )
        for workorder in self.filtered(
            lambda x: x.state == "done"
            and (
                not x.time_ids
                or (
                    (100 - x.duration_percent)
                    <= x.production_id.company_id.minimum_order_time_threshold
                )
            )
            and x.production_id.company_id.use_projected_time_work_orders
        ):
            # FIX ME: this is because duration expected use this field to compute
            workorder.qty_production = workorder.qty_produced
            workorder.duration_expected = workorder._get_duration_expected()
            workorder.add_time_to_work_order(fully_productive_time)
            if (
                100 - workorder.duration_percent
            ) > workorder.production_id.company_id.maximum_order_time_threshold:
                workorder.reduce_time_to_workorder(fully_productive_time)
        return res
