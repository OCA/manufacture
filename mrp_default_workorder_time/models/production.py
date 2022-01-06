# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    def add_time_to_work_order(self, fully_productive_time, workorder):
        workorder._compute_duration()
        date_start = workorder.date_planned_start
        if not date_start:
            raise UserError(
                _(
                    "You should plan orders to set default "
                    "production time on work orders, please check"
                )
            )
        date_end = workorder.date_planned_start + relativedelta(
            minutes=workorder.duration_expected
        )
        if workorder.time_ids:
            minutes_to_add = workorder.duration_expected - workorder.duration
            if float_compare(minutes_to_add, 0, precision_digits=6) == -1:
                return
            date_start = max(workorder.time_ids.mapped("date_end"))
            date_end = date_start + relativedelta(minutes=minutes_to_add)
        workorder.write(
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
                            "workcenter_id": workorder.workcenter_id.id,
                            "description": fully_productive_time.name,
                        },
                    )
                ]
            }
        )

    def reduce_time_to_workorder(self, fully_productive_time, workorder):
        workorder.time_ids.filtered(
            lambda x: x.loss_id.id == fully_productive_time.id
        ).sudo().unlink()
        self.add_time_to_work_order(fully_productive_time, workorder)

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
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
        for rec in self.filtered(lambda x: x.company_id.use_projected_time_work_orders):
            for workorder in rec.workorder_ids.filtered(
                lambda x: not x.time_ids
                or (
                    (100 - x.duration_percent)
                    <= rec.company_id.minimum_order_time_threshold
                )
            ):
                self.add_time_to_work_order(fully_productive_time, workorder)
            for workorder in rec.workorder_ids.filtered(
                lambda x: (100 - x.duration_percent)
                > rec.company_id.maximum_order_time_threshold
            ):
                self.reduce_time_to_workorder(fully_productive_time, workorder)
        return res
