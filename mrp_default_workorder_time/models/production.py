# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):

    _inherit = "mrp.production"

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
            rec.workorder_ids._compute_duration()
            for workorder in rec.workorder_ids.filtered(
                lambda x: not x.time_ids
                or (
                    (100 - x.duration_percent)
                    <= rec.company_id.minimum_order_time_threshold
                )
            ):
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
                    date_start = max(workorder.time_ids.mapped("date_end"))
                    date_end = date_start + relativedelta(
                        minutes=workorder.duration_expected - workorder.duration
                    )
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
        return res
