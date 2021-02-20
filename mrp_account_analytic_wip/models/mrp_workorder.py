# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MRPWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    @api.depends("analytic_product_id.standard_price")
    def _compute_onchange_costs_hour(self):
        """
        When using Cost Type Product, set the corresponding standard cost
        and the work center hourly cost
        """
        for wc in self:
            standard_cost = wc.analytic_product_id.standard_price
            if standard_cost:
                wc.costs_hour = standard_cost

    analytic_product_id = fields.Many2one(
        "product.product", string="Cost Type", domain="[('is_cost_type', '=', True)]"
    )
    costs_hour = fields.Float(
        compute="_compute_onchange_costs_hour", store=True, readonly=False
    )


class MRPWorkOrder(models.Model):
    _name = "mrp.workorder"
    _inherit = ["mrp.workorder", "account.analytic.tracked.mixin"]

    def _prepare_mrp_workorder_analytic_item(self):
        """
        Prepare additional values for Analytic Items created.
        For compatibility with analytic_activity_cost
        """
        values = super()._prepare_mrp_workorder_analytic_item()
        values.update(
            {
                "analytic_tracking_item_id": self.analytic_tracking_item_id.id,
            }
        )
        return values

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
