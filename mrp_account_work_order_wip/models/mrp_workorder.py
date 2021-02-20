# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class MRPWorkOrder(models.Model):
    _inherit = ["mrp.workorder", "account.analytic.tracked.mixin"]

    def _compute_tracked_planned_amount(self):
        super()._compute_tracked_planned_amount()
        for item in self:
            hours = item.expected_duration / 60
            unit_cost = item.workcenter_id.costs_hour
            item.tracked_planned_amount = hours * unit_cost

    def _prepare_tracking_item_domain(self):
        self.ensure_one()
        return [("workorder_id", "=", self.id)]

    def _prepare_tracking_item_values(self):
        self.ensure_one()
        return {
            "analytic_id": self.production_id.analytic_account_id.id,
            "product_id": self.workcenter_id.analytic_product_id.id,
            "workorder_id": self.id,
        }
