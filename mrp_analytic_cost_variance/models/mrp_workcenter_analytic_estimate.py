from odoo import api, fields, models


class WorkCenterAnalyticEstimate(models.Model):
    _name = "mrp.workcenter.analytic.estimate"
    _description = "Work Center Analytic Estimate"
    _rec_name = "work_order_id"

    @api.depends("factor")
    def _compute_calc_quantity_estimate(self):
        for record in self:
            self.quantity_estimate = (
                record.work_order_id.duration_expected * record.factor
            )

    @api.depends("unit_cost", "quantity_estimate")
    def _compute_calc_cost_estimate(self):
        for record in self:
            self.cost_estimate = record.unit_cost * record.quantity_estimate

    @api.depends("analytic_account_id", "analytic_line_ids")
    def _compute_calc_cost_quantity_actual(self):
        # FIXME: computed stored filed will create a transaction bottleneck!
        AnalyticLine = self.env["account.analytic.line"]
        for record in self:
            # FIXME: optimize using read_group before th for loop
            lines = AnalyticLine.search_read(
                [("account_id", "=", record.analytic_account_id.id)],
                ["amount", "unit_amount"],
            )
            self.cost_actual = sum([r["amount"] for r in lines])
            self.quantity_actual = sum([r["unit_amount"] for r in lines])

    @api.depends("quantity_estimate", "cost_estimate", "cost_actual", "quantity_actual")
    def _compute_calc_variance(self):
        for record in self:
            self.cost_variance = record.cost_actual - record.cost_estimate
            self.quantity_variance = record.quantity_actual - record.quantity_estimate

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
    # TODO: confirm it is useful to keep this One2many field
    analytic_line_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="workcenter_analytic_estimate_id",
    )
    factor = fields.Float(string="Factor", default=1.0)
    unit_cost = fields.Float(string="Unit Cost (Estimate)")
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
        # store=True,  # FIXME
    )
    quantity_actual = fields.Float(
        compute="_compute_calc_cost_quantity_actual",
        string="Quantity (Actual)",
        # store=True,  # FIXME
    )
    quantity_variance = fields.Float(
        compute="_compute_calc_variance",
        string="Quantity (Variance)",
        # store=True,  # FIXME
    )
    cost_variance = fields.Float(
        compute="_compute_calc_variance",
        string="Cost (Variance)",
        # store=True,  # FIXME
    )
