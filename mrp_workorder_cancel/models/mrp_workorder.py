# Copyright (C) 2023 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_workorder_cancel_undo(self):
        for wo in self:
            if wo.state not in "cancel":
                raise UserError(_("Only Cancel Work Order Can Reset to Ready State."))
            else:
                wo.write({"state": "ready"})
                wo.action_replan()
