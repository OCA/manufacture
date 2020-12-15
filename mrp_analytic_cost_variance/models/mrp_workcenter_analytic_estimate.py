from odoo import api, fields, models


class WorkCenterAnalyticEstimate(models.Model):
    _name = "mrp.workcenter.analytic.estimate"
    _description = "Work center analytic estimate"
    _rec_name = "work_order_id"

    @api.depends("factor")
    def _compute_calc_quantity_estimate(self):
        quantity = 0.0
        for record in self:
            quantity += record.work_order_id.duration_expected * record.factor
        self.quantity_estimate = quantity

    @api.depends("unit_cost", "quantity_estimate")
    def _compute_calc_cost_estimate(self):
        cost = 0.0
        for record in self:
            cost += record.unit_cost * record.quantity_estimate
        self.cost_estimate = cost

    @api.depends("analytic_account_id")
    def _compute_calc_cost_quantity_actual(self):
        cost = 0.0
        quantity = 0.0
        analytic_line_obj = self.env["account.analytic.line"]
        for record in self:
            lines = analytic_line_obj.search_read(
                [("account_id", "=", record.analytic_account_id.id)],
                ["amount", "unit_amount"],
            )
            cost += sum([r["amount"] for r in lines])
            quantity += sum([r["unit_amount"] for r in lines])
        self.cost_actual = cost
        self.quantity_actual = quantity

    @api.depends("quantity_estimate", "cost_estimate", "cost_actual", "quantity_actual")
    def _compute_calc_variance(self):
        quantity = 0.0
        cost = 0.0
        for record in self:
            cost += record.cost_actual - record.cost_estimate
            quantity += record.quantity_actual - record.quantity_estimate
        self.cost_variance = cost
        self.quantity_variance = quantity

    work_order_id = fields.Many2one(
        "mrp.workorder",
        string="Work Order",
    )
    manufacturing_order_id = fields.Many2one(
        related="work_order_id.production_id", string="Manufacture Order", store=True
    )
    analytic_account_id = fields.Many2one(
        related="work_order_id.production_id.analytic_account_id",
        string="Analytic Account",
        store=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    product_category_id = fields.Many2one(
        related="product_id.categ_id", string="Product Category", store=True
    )
    factor = fields.Float(string="Factor", default=1.0)
    unit_cost = fields.Float(
        related="product_id.standard_price",
        string="Unit Cost (Estimate)",
        store=True,
    )
    quantity_estimate = fields.Float(
        compute="_compute_calc_quantity_estimate",
        string="Quantity (Estimate)",
        store=True,
    )
    cost_estimate = fields.Float(
        compute="_compute_calc_cost_estimate",
        string="Cost (Estimate)",
        store=True,
    )
    cost_actual = fields.Float(
        compute="_compute_calc_cost_quantity_actual",
        string="Cost (Actual)",
        store=True,
    )
    quantity_actual = fields.Float(
        compute="_compute_calc_cost_quantity_actual",
        string="Quantity (Actual)",
        store=True,
    )
    quantity_variance = fields.Float(
        compute="_compute_calc_variance",
        string="Quantity (Variance)",
        store=True,
    )
    cost_variance = fields.Float(
        compute="_compute_calc_variance",
        string="Cost (Variance)",
        store=True,
    )
