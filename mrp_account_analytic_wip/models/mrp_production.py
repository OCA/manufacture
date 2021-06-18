# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, fields, models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    analytic_tracking_item_count = fields.Integer(
        "WIP Item Count", compute="_compute_analytic_tracking_item"
    )
    analytic_tracking_item_amount = fields.Integer(
        "WIP Actual Amount", compute="_compute_analytic_tracking_item"
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    def _get_tracking_items(self):
        """
        Returns a recordset with the related Ttacking Items
        """
        return (
            self.mapped("move_raw_ids.analytic_tracking_item_id")
            | self.mapped("workorder_ids.analytic_tracking_item_id")
            | self.mapped("workorder_ids.analytic_tracking_item_id.child_ids")
        )

    def _compute_analytic_tracking_item(self):
        for mo in self:
            tracking_items = mo._get_tracking_items()
            mo.analytic_tracking_item_count = len(tracking_items)
            mo.analytic_tracking_item_amount = sum(
                tracking_items.mapped("actual_amount")
            )

    def action_view_analytic_tracking_items(self):
        self.ensure_one()
        return {
            "res_model": "account.analytic.tracking.item",
            "type": "ir.actions.act_window",
            "name": _("%s Tracking Items") % self.name,
            "domain": [("id", "in", self._get_tracking_items().ids)],
            "view_mode": "tree,form",
        }

    def action_confirm(self):
        """
        On MO Confirm, save the planned amount on the tracking item.
        Note that in some cases, the Analytic Account might be set
        just after MO confirmation.
        """
        res = super().action_confirm()
        self.mapped("move_raw_ids").set_tracking_item(update_planned=True)
        self.mapped("workorder_ids").set_tracking_item(update_planned=True)
        return res

    def write(self, vals):
        """
        When setting the Analytic account,
        generate tracking items.

        On MTO, the Analytic Account might be set after the action_confirm(),
        so the planned amount needs to be set here.

        TODO: in what cases the planned amounts update should be prevented?
        """
        res = super().write(vals)
        # FIXME: adding non planned lines should create zero budget tracking items
        if "analytic_account_id" in vals:
            update_planned = any(x.state == "confirmed" for x in self)
            tracking_items = self._get_tracking_items()
            tracking_items.write({"analytic_id": vals["analytic_account_id"]})
            tracking_items.child_ids.write({"analytic_id": vals["analytic_account_id"]})
            self.move_raw_ids.set_tracking_item(update_planned=update_planned)
            self.workorder_ids.set_tracking_item(update_planned=update_planned)
        return res

    def button_mark_done(self):
        res = super().button_mark_done()
        mfg_done = self.filtered(lambda x: x.state == "done")
        tracking_items = mfg_done._get_tracking_items()
        tracking_items.process_wip_and_variance(close=True)
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self._get_tracking_items().action_cancel()
        return res

    def copy(self, default=None):
        new = super().copy(default=default)
        new.move_raw_ids.set_tracking_item()
        new.workorder_ids.set_tracking_item()
        return new
