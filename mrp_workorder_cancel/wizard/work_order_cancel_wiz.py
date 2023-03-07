# Copyright (C) 2023 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class WorkOrderCancelWiz(models.TransientModel):

    _name = "work.order.cancel.wiz"

    def action_cancel_work_order(self):
        work_order_id = self.env["mrp.workorder"].browse(self.env.context["active_id"])
        work_order_id.action_cancel()
        return True
