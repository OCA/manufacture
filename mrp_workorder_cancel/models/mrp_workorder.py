# Copyright (C) 2023 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_cancel(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_workorder_cancel.action_work_order_cancel_confirm"
        )
        return action

    def button_workorder_cancel_undo(self):
        work_order_ids = self.env["mrp.workorder"].browse(
            self.env.context.get("active_ids")
        )
        for wo in work_order_ids:
            if wo.state not in "cancel":
                raise UserError(_("Only Cancel Work Order Can Reset to Ready State."))
            else:
                wo.write({"state": "ready"})
                wo.action_replan()
