# Copyright (C) 2020 Open Source Integrators
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


class MRPWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _prepare_mrp_workorder_analytic_item(self):
        self.ensure_one()
        return {
            "name": "{} / {}".format(self.production_id.name, self.name),
            "account_id": self.production_id.analytic_account_id.id,
            "date": fields.Date.today(),
            "company_id": self.company_id.id,
            "manufacturing_order_id": self.production_id.id,
            "product_id": self.workcenter_id.analytic_product_id.id,
            "unit_amount": self.duration / 60,  # convert minutes to hours
            "workorder_id": self.id,
        }

    def generate_mrp_work_analytic_line(self):
        """Generate Analytic Lines"""
        AnalyticLine = self.env["account.analytic.line"].sudo()
        workorders = self.filtered("workcenter_id.analytic_product_id").filtered(
            "production_id.analytic_account_id"
        )
        existing_items = workorders and AnalyticLine.search(
            [("workorder_id", "in", self.ids)]
        )
        for workorder in workorders:
            line_vals = self._prepare_mrp_workorder_analytic_item()
            analytic_lines = existing_items.filtered(
                lambda x: x.workorder_id == workorder
            )
            if analytic_lines:
                for analytic_line in analytic_lines:
                    analytic_line.write(line_vals)
                    analytic_line.on_change_unit_amount()
            else:
                analytic_line = AnalyticLine.create(line_vals)
                analytic_line.on_change_unit_amount()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("duration"):
            res.generate_mrp_work_analytic_line()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("duration"):
            self.generate_mrp_work_analytic_line()
        return res
