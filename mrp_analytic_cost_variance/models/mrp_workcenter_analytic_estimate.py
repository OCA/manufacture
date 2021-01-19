from odoo import api, fields, models


class MrpAnalyticEstimate(models.Model):
    _name = "mrp.analytic.estimate"
    _description = "Manufacturing Analytic Estimate"
    _rec_name = "production_id"

    @api.depends("unit_cost", "quantity_estimate")
    def _compute_amount_estimate(self):
        for record in self:
            record.cost_estimate = record.unit_cost * record.quantity_estimate

    @api.depends(
        "analytic_account_id", "production_id", "work_order_id", "stock_move_id"
    )
    def _compute_calc_cost_quantity_actual(self):
        # FIXME: computed stored field will create a transaction bottleneck!
        AnalyticItem = self.env["account.analytic.line"].sudo()
        all_items = AnalyticItem.search(
            [("manufacturing_order_id", "in", self.mapped("production_id").ids)]
        )
        for record in self:
            if record.stock_move_id:
                items = all_items.filtered(
                    lambda x: x.stock_move_id == record.stock_move_id
                )
            else:
                items = all_items.filtered(
                    lambda x: x.workorder_id == record.work_order_id
                )
            # Do not sum amounts for parent Cost Types, to avoid duplication
            record.cost_actual = -sum([x.amount for x in items if not x.child_ids])
            # Do not sum qty for child Cost Types, to avoid duplication
            record.quantity_actual = sum(
                [
                    x.unit_amount
                    for x in items
                    if not (x.product_id.is_cost_type and not x.child_ids)
                ]
            )

    @api.depends("quantity_estimate", "cost_estimate", "cost_actual", "quantity_actual")
    def _compute_calc_variance(self):
        for record in self:
            record.cost_variance = record.cost_actual - record.cost_estimate
            record.quantity_variance = record.quantity_actual - record.quantity_estimate

    production_id = fields.Many2one("mrp.production", string="Manufacture Order")
    analytic_account_id = fields.Many2one(
        related="production_id.analytic_account_id",
        string="Analytic Account",
        store=True,
    )
    product_id = fields.Many2one("product.product", string="Product")
    product_category_id = fields.Many2one(
        related="product_id.categ_id", string="Product Category", store=True
    )
    work_order_id = fields.Many2one("mrp.workorder", string="Work Order")
    stock_move_id = fields.Many2one("stock.move", string="Material Component")

    # Estimates
    unit_cost = fields.Float(string="Unit Cost (Estimate)")
    quantity_estimate = fields.Float("Qty (Est.)")
    cost_estimate = fields.Float(
        compute="_compute_amount_estimate", string="Cost (Est.)", store=True
    )

    # Actuals
    cost_actual = fields.Float(
        compute="_compute_calc_cost_quantity_actual",
        string="Cost (Act.)",
        # store=True,  # FIXME
    )
    quantity_actual = fields.Float(
        compute="_compute_calc_cost_quantity_actual",
        string="Quantity (Act.)",
        # store=True,  # FIXME
    )

    # Variances
    quantity_variance = fields.Float(
        compute="_compute_calc_variance",
        string="Quantity (Var.)",
        # store=True,  # FIXME
    )
    cost_variance = fields.Float(
        compute="_compute_calc_variance",
        string="Cost (Var.)",
        # store=True,  # FIXME
    )
