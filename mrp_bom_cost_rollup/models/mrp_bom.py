# Copyright 2026 Cubiczan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currency_id",
        help="Company currency used to express the rolled-up cost.",
    )
    bom_cost = fields.Monetary(
        string="BoM Cost",
        compute="_compute_bom_cost",
        currency_field="currency_id",
        help="Rolled-up cost to produce one batch (the BoM quantity) of the "
        "product: the sum of component costs — recursively through sub-BoMs — "
        "plus operation costs.",
    )
    bom_unit_cost = fields.Monetary(
        string="BoM Unit Cost",
        compute="_compute_bom_cost",
        currency_field="currency_id",
        help="BoM Cost divided by the BoM quantity: the rolled-up cost of a "
        "single unit of the produced product.",
    )

    @api.depends("company_id")
    def _compute_currency_id(self):
        main_currency = self.env.company.currency_id
        for bom in self:
            bom.currency_id = bom.company_id.currency_id or main_currency

    @api.depends(
        "product_qty",
        "bom_line_ids.product_qty",
        "bom_line_ids.product_uom_id",
        "bom_line_ids.product_id.standard_price",
        "bom_line_ids.child_bom_id",
        "operation_ids.time_cycle_manual",
        "operation_ids.workcenter_id.costs_hour",
        "currency_id",
    )
    def _compute_bom_cost(self):
        for bom in self:
            batch_cost = bom._get_bom_cost()
            qty = bom.product_qty or 1.0
            bom.bom_cost = batch_cost
            bom.bom_unit_cost = batch_cost / qty

    def _get_bom_cost(self, visited=None):
        """Return the cost to produce ``product_qty`` units of the BoM product.

        :param visited: set of BoM ids already in the current branch, used to
            short-circuit the (illegal but possible) case of a BoM that
            references itself through its sub-BoMs.
        """
        self.ensure_one()
        if visited is None:
            visited = set()
        if self.id in visited:
            return 0.0
        visited = visited | {self.id}
        return self._get_components_cost(visited) + self._get_operations_cost()

    def _get_components_cost(self, visited):
        self.ensure_one()
        total = 0.0
        for line in self.bom_line_ids:
            # Normalise the line quantity to the component's reference UoM,
            # which is the unit `standard_price` is expressed in.
            qty = line.product_uom_id._compute_quantity(
                line.product_qty, line.product_id.uom_id
            )
            child_bom = line.child_bom_id
            if child_bom:
                child_qty = child_bom.product_qty or 1.0
                unit_cost = child_bom._get_bom_cost(visited) / child_qty
            else:
                unit_cost = line.product_id.standard_price
            total += unit_cost * qty
        return total

    def _get_operations_cost(self):
        self.ensure_one()
        total = 0.0
        for operation in self.operation_ids:
            costs_hour = operation.workcenter_id.costs_hour
            if not costs_hour:
                continue
            total += (operation.time_cycle_manual / 60.0) * costs_hour
        return total

    def action_set_standard_price_from_bom(self):
        """Write the rolled-up unit cost into the produced product's cost."""
        for bom in self:
            product = bom.product_id or bom.product_tmpl_id
            product.sudo().write({"standard_price": bom.bom_unit_cost})
        return True
