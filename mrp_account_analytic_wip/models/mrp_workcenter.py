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
        "product.product", string="Cost Product", domain="[('type', '=', 'service')]"
    )
    costs_hour = fields.Float(
        compute="_compute_onchange_costs_hour", store=True, readonly=False
    )
