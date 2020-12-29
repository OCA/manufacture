#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SwitchScheduleState(models.TransientModel):
    _name = "switch.schedule_state"
    _description = "Allow to switch the schedule state"

    @api.model
    def _get_state(self):
        active_ids = self.env.context.get("active_ids", [])
        manufacturing_orders = self.env["mrp.production"].browse(active_ids)
        result = manufacturing_orders._get_values_from_selection("schedule_state")
        return result

    schedule_state = fields.Selection(
        selection=_get_state, string="Schedule State", required=True
    )
    date_planned_start = fields.Datetime(
        help="If left empty, manufacture order will be schedule at current datetime"
    )

    @api.constrains("schedule_state", "date_planned_start")
    def check_date_planned_start(self):
        for _wiz in self:
            if self.schedule_state != "scheduled" and self.date_planned_start:
                raise UserError(
                    _(
                        "It is not possible to put a schedule date without "
                        "changing the state to scheduled."
                    )
                )

    def switch_schedule_state(self):
        """
        It is possible to schedule waiting MO in advance (before it is
        at todo state) In that case, the state stays waiting but
        the schedule date is set. It schedule state automatically
        will go to scheduled once the MO is ready.
        """
        self.ensure_one()
        MrpProduction = self.env["mrp.production"]
        active_ids = self.env.context.get("active_ids", [])
        if isinstance(active_ids, int):
            active_ids = [active_ids]
        vals = {}
        if self.date_planned_start:
            # forbid to schedule in the past
            now = datetime.now()
            # If we don't let a margin to the user, he won't ever be able
            # to put the now datetime in the wizard and validate because
            # It take time to click on the wizard validation button!
            now_with_margin = now - timedelta(minutes=10)
            if self.date_planned_start < now_with_margin:
                raise UserError(
                    _(
                        "It is not possible to schedule Manufacture Orders "
                        "In the past."
                    )
                )
            vals = {
                "date_planned_start": self.date_planned_start,
                "schedule_user_id": self.env.user.id,
            }
        manufacturing_orders = MrpProduction.browse(active_ids)
        if self.schedule_state == "scheduled":
            waiting_mo = MrpProduction.search(
                [("id", "in", active_ids), ("schedule_state", "=", "waiting")]
            )
            if waiting_mo:
                if not self.date_planned_start:
                    raise UserError(
                        _(
                            "It is not possible to schedule waiting MOs without "
                            "a Scheduled Date in the future"
                        )
                    )
                waiting_mo.write(vals)
            manufacturing_orders -= waiting_mo
        vals["schedule_state"] = self.schedule_state
        manufacturing_orders.write(vals)
