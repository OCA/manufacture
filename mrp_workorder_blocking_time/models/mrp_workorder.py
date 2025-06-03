# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, fields, models
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    blocking_stage_end = fields.Datetime(copy=False)
    blocking_period_interrupted = fields.Boolean(copy=False)
    interruption_reason = fields.Text(copy=False)

    def unlink(self):
        for wo in self:
            if (
                wo.state == "progress"
                and wo.operation_id
                and wo.operation_id.blocking_stage is True
            ):
                raise UserError(_("You cannot remove a blocking operation!"))
        return super(MrpWorkorder, self).unlink()

    def button_start(self):
        res = super().button_start()
        if self.operation_id and self.operation_id.blocking_stage is True:
            # calculate the end of the blocking stage based on :
            # the recommended_blocking_time from operation_id + the start date of the work order
            blocking_stage_end = self.date_start + timedelta(
                hours=self.operation_id.recommended_blocking_time
            )
            self.blocking_stage_end = blocking_stage_end
        return res

    def _open_blocking_reason_popup(self, action_to_do):
        action = self.env.ref(
            "mrp_workorder_blocking_time.mrp_workorder_blocking_reason_wizard_act_window"
        ).read()[0]
        action["context"] = {"active_id": self.id, "action_to_do": action_to_do}
        return action

    def _check_blocking_time_done(self):
        """
        This method check if the blocking stage is done
        """
        for wo in self:
            if (
                wo.state not in ("done", "cancel")
                and wo.operation_id
                and wo.operation_id.blocking_stage is True
            ):
                if wo.blocking_stage_end:
                    if wo.blocking_stage_end > fields.Datetime.now():
                        wo.blocking_period_interrupted = True
                        return True
        return False

    def button_pending(self):
        bypass_check_blocking_time = self.env.context.get(
            "bypass_check_blocking_time", False
        )
        if bypass_check_blocking_time is True:
            return super().button_pending()
        show_warning_popup = self._check_blocking_time_done()
        if show_warning_popup is True:
            return self._open_blocking_reason_popup("button_pending")
        return super().button_pending()

    def button_finish(self):
        bypass_check_blocking_time = self.env.context.get(
            "bypass_check_blocking_time", False
        )
        if bypass_check_blocking_time is True:
            return super().button_finish()
        show_warning_popup = self._check_blocking_time_done()
        if show_warning_popup is True:
            return self._open_blocking_reason_popup("button_finish")
        res = super().button_finish()
        return res

    def do_finish(self):
        bypass_check_blocking_time = self.env.context.get(
            "bypass_check_blocking_time", False
        )
        if bypass_check_blocking_time is True:
            return super().do_finish()
        show_warning_popup = self._check_blocking_time_done()
        if show_warning_popup is True:
            return self._open_blocking_reason_popup("do_finish")
        res = super().do_finish()
        return res

    def action_open_manufacturing_order(self):
        bypass_check_blocking_time = self.env.context.get(
            "bypass_check_blocking_time", False
        )
        if bypass_check_blocking_time is True:
            return super().action_open_manufacturing_order()
        show_warning_popup = self._check_blocking_time_done()
        if show_warning_popup is True:
            return self._open_blocking_reason_popup("action_open_manufacturing_order")
        res = super().action_open_manufacturing_order()
        return res
