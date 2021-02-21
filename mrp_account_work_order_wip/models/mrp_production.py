# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        """
        On MO Confirm, save the planned amount
        on the tracking item
        """
        res = super().action_confirm()
        self.mapped("workorder_ids").set_tracking_item(update_planned=True)
        return res

    def write(self, vals):
        """
        When setting the Analytic account,
        generate tracking items
        """
        res = super().write(vals)
        if "analytic_account_id" in vals:
            self.workorder_ids.set_tracking_item()
        return res
