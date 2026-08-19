# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    currency_id = fields.Many2one(related="product_tmpl_id.currency_id")

    # Fields related to standard price
    product_standard_price = fields.Float(compute="_compute_product_standard_price")
    standard_price = fields.Float(
        string="BoM Unit Cost",
        tracking=True,
        digits="Product Price",
        compute="_compute_standard_price",
        help="Calculated with raw components cost divided by the BoM quantity.",
    )
    diff_product_bom_standard_price = fields.Boolean(
        compute="_compute_diff_product_bom_standard_price",
        help="Technical field used to display or hide button 'Apply this cost "
        "to Product standard price' in the form view",
    )

    # Fields related to sale price
    product_sale_price = fields.Float(
        string="Product Sale Price", related="product_tmpl_id.list_price"
    )
    product_margin_rate = fields.Float(related="product_tmpl_id.standard_margin_rate")

    cost_basis = fields.Selection(
        selection=[
            ("direct", "Direct (this BoM level only)"),
            ("rolled_up", "Rolled-up (sub-BoMs + operations)"),
        ],
        default="direct",
        required=True,
        help="How the BoM Unit Cost is computed.\n"
        "Direct: sum of the components' own cost (standard price), this level only "
        "— use when you maintain costs bottom-up, updating each level yourself.\n"
        "Rolled-up: recurse through sub-BoMs and add operation/work-center costs in "
        "one pass. Components without a BoM fall back to their standard price, so it "
        "reconciles with Direct once all sub-costs are maintained.",
    )

    # Compute functions
    @api.depends("product_tmpl_id", "product_tmpl_id.standard_price")
    def _compute_product_standard_price(self):
        for bom in self:
            bom.product_standard_price = bom.product_tmpl_id.standard_price

    @api.depends(
        "product_tmpl_id",
        "bom_line_ids",
        "bom_line_ids.standard_price_subtotal",
        "product_qty",
        "cost_basis",
        "operation_ids.time_cycle_manual",
        "operation_ids.workcenter_id.costs_hour",
    )
    def _compute_standard_price(self):
        for bom in self:
            qty = bom.product_qty if bom.product_qty != 0 else 1
            total = sum(x.standard_price_subtotal for x in bom.bom_line_ids)
            if bom.cost_basis == "rolled_up":
                total += bom._get_operations_cost()
            bom.standard_price = total / qty

    def _get_operations_cost(self):
        self.ensure_one()
        return sum(
            (op.time_cycle_manual / 60.0) * op.workcenter_id.costs_hour
            for op in self.operation_ids
            if op.workcenter_id.costs_hour
        )

    def _get_rolled_up_batch_cost(self, visited=None):
        """Cost to produce product_qty units: recursive component costs + operations.
        Always rolls up (independent of each BoM's own cost_basis)."""
        self.ensure_one()
        if visited is None:
            visited = set()
        if self.id in visited:
            return 0.0
        visited = visited | {self.id}
        total = 0.0
        for line in self.bom_line_ids:
            child = line.child_bom_id
            if child:
                unit = child._get_rolled_up_batch_cost(visited) / (
                    child.product_qty or 1.0
                )
            else:
                unit = line.product_id.standard_price
            total += unit * line.product_qty
        return total + self._get_operations_cost()

    @api.depends("product_tmpl_id.standard_price", "standard_price")
    def _compute_diff_product_bom_standard_price(self):
        price_dp = self.env["decimal.precision"].precision_get("Product Price")
        for bom in self:
            if bom.product_tmpl_id:
                diff = bom.product_tmpl_id.standard_price - bom.standard_price
                bom.diff_product_bom_standard_price = float_round(diff, price_dp)
            else:
                bom.diff_product_bom_standard_price = False

    # Functions to change product fields
    def set_product_standard_price(self):
        for bom in self.filtered(lambda x: x.product_tmpl_id):
            bom.product_tmpl_id.standard_price = bom.standard_price
