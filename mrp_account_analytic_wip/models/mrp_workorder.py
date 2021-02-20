# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MRPWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item", string="Tracking Item", copy=False
    )
    # Operations added after MO confirmation have expected qty zero
    duration_expected = fields.Float(default=0.0)
    # Make MO lock status available for views
    is_locked = fields.Boolean(related="production_id.is_locked")
    duration_planned = fields.Float(string="Planned Duration")

    def _prepare_tracking_item_values(self):
        analytic = self.production_id.analytic_account_id
        planned_qty = self.duration_planned / 60
        return analytic and {
            "analytic_id": analytic.id,
            "product_id": self.workcenter_id.analytic_product_id.id,
            "workorder_id": self.id,
            "planned_qty": planned_qty,
        }

    def populate_tracking_items(self, set_planned=False):
        """
        When creating a Work Order link it to a Tracking Item.
        It may be an existing Tracking Item,
        or a new one my be created if it doesn't exist yet.
        """
        TrackingItem = self.env["account.analytic.tracking.item"]
        to_populate = self.filtered(
            lambda x: x.production_id.analytic_account_id
            and x.production_id.state not in ("draft", "done", "cancel")
        )
        all_tracking = to_populate.production_id.analytic_tracking_item_ids
        for item in to_populate:
            tracking = all_tracking.filtered(lambda x: x.workorder_id == self)[:1]
            vals = item._prepare_tracking_item_values()
            not set_planned and vals.pop("planned_qty")
            if tracking:
                tracking.write(vals)
            else:
                tracking = TrackingItem.create(vals)
            item.analytic_tracking_item_id = tracking

    @api.model
    def create(self, vals):
        new_workorder = super().create(vals)
        new_workorder.populate_tracking_items()
        return new_workorder


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    def _prepare_mrp_workorder_analytic_item(self, duration):
        values = super()._prepare_mrp_workorder_analytic_item(duration=duration)
        values["product_id"] = self.workcenter_id.analytic_product_id.id
        return values
