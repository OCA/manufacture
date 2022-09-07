from odoo import _, fields, models
from odoo.exceptions import UserError


class WizardBlockingReason(models.TransientModel):
    _name = "mrp.workorder.blocking.reason.wizard"
    _description = "Wizard to open a blocking reason popup for a workorder"

    interruption_reason = fields.Text(copy=False)

    def action_confirm(self):
        """
        This method allow to set the interruption reason on the workorder
        """
        self.ensure_one()
        action_to_do = self.env.context.get("action_to_do")
        if not action_to_do:
            raise UserError(_("No action to do"))
        workorder_obj = self.env["mrp.workorder"]
        workorder = workorder_obj.browse(self.env.context.get("active_id"))
        workorder.interruption_reason = self.interruption_reason
        workorder.blocking_period_interrupted = bool(self.interruption_reason)
        if hasattr(workorder, action_to_do):
            getattr(
                workorder.with_context(bypass_check_blocking_time=True), action_to_do
            )()
        return {"type": "ir.actions.act_window_close"}
