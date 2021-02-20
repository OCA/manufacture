# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class MRPWorkOrder(models.Model):
    _name = "mrp.workorder"
    _inherit = ["mrp.workorder", "account.analytic.tracked.mixin"]

    def _prepare_mrp_workorder_analytic_item(self):
        """
        Prepare additional values for Analytic Items created.
        For compatibility with analytic_activity_cost
        """
        self.ensure_one()
        vals = super()._prepare_mrp_workorder_analytic_item()
        vals["analytic_tracking_item_id"] = self.analytic_tracking_item_id.id
        return vals

    def _get_tracking_planned_qty(self):
        super()._get_tracking_planned_qty()
        return self.duration_expected / 60

    def _prepare_tracking_item_values(self):
        vals = super()._prepare_tracking_item_values()
        analytic = self.production_id.analytic_account_id
        if analytic:
            vals.update(
                {
                    "analytic_id": analytic.id,
                    "product_id": self.workcenter_id.analytic_product_id.id,
                    "workorder_id": self.id,
                }
            )
        return vals
