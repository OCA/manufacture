# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        """
        On MO Confirm, save the planned amount on the tracking item.
        """
        res = super().action_confirm()
        self.mapped("move_raw_ids").set_tracking_item(update_planned=True)
        return res

    def write(self, vals):
        """
        When setting the Analytic account,
        generate tracking items
        """
        res = super().write(vals)
        if "analytic_account_id" in vals:
            self.move_raw_ids.set_tracking_item()
        return res

    def process_wip_and_variance_on_done(self):
        mfg_done = self.filtered(lambda x: x.state == "done")
        if mfg_done:
            tracking_items = mfg_done.mapped(
                "move_raw_ids.analytic_tracking_item_id"
            ) | mfg_done.mapped("workorder_ids.analytic_tracking_item_id")
            tracking_items.process_wip_and_variance_on_done()

    def button_mark_done(self):
        res = super().button_mark_done()
        self.process_wip_and_variance_on_done()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        # TODO: what to do if there are JEs done?
        return res
