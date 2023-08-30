# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AnalyticTrackingItem(models.Model):
    _inherit = "account.analytic.tracking.item"

    stock_move_id = fields.Many2one(
        "stock.move", string="Stock Move", ondelete="cascade"
    )
    # FIXME: remove workorder, as Tracking Items should be per Work Center
    workorder_id = fields.Many2one(
        "mrp.workorder", string="Work Order", ondelete="cascade"
    )
    workcenter_id = fields.Many2one(
        "mrp.workcenter", string="Work Center", ondelete="cascade"
    )
    production_id = fields.Many2one(
        "mrp.production", string="Manufacturing Order", ondelete="cascade"
    )
    actual_stock_move_ids = fields.One2many("stock.move", "analytic_tracking_item_id")
    actual_workorder_ids = fields.One2many("mrp.workorder", "analytic_tracking_item_id")

    # Requested quantity to be manufactured
    requested_qty = fields.Float()
    requested_amount = fields.Float()

    @api.depends(
        "stock_move_id.product_id",
        "workorder_id.display_name",
        "workorder_id.workcenter_id",
        "workcenter_id.name",
    )
    def _compute_name(self):
        res = super()._compute_name()
        for tracking in self:
            is_child = tracking.parent_id
            if tracking.stock_move_id:
                move = tracking.stock_move_id
                tracking.name = "{}{} / {}".format(
                    "-> " if is_child else "",
                    move.product_id.display_name,
                    move.raw_material_production_id.name,
                )
            elif tracking.workorder_id:
                workorder = tracking.workorder_id
                tracking.name = "{} {} {}".format(
                    "-> " if is_child else "",
                    "" if is_child else workorder.workcenter_id.name,
                    tracking.product_id.default_code if is_child else "",
                )
            elif tracking.workcenter_id:
                workcenter = tracking.workcenter_id
                tracking.name = "{} {} {}".format(
                    "-> " if is_child else "",
                    "" if is_child else workcenter.name,
                    tracking.product_id.default_code if is_child else "",
                )
        return res

    def _prepare_account_move_head(self, journal, move_lines=None, ref=None):
        """
        Preserve related Stock Move, needed to compute the "Is WIP" flag on J.Items.
        """
        res = super()._prepare_account_move_head(
            journal, move_lines=move_lines, ref=ref
        )
        res["stock_move_id"] = self.stock_move_id.id
        return res

    def _get_accounting_data_for_valuation(self):
        """
        For raw material stock moves, consider the destination location (Production)
        input and output accounts.
        - "stock_input": is the WIP account where consumption is expected to have been
          posted
        - "stock_variance": is the Variance account
        """
        accounts = super()._get_accounting_data_for_valuation()
        dest_location = self.stock_move_id.location_dest_id or (
            self.product_id.type == "product"
            and self.product_id.property_stock_production
        )
        # Only set for raw materials
        if dest_location and dest_location.valuation_in_account_id:
            accounts["stock_input"] = dest_location.valuation_in_account_id
            accounts["stock_wip"] = accounts["stock_input"]
            accounts["stock_variance"] = dest_location.valuation_variance_account_id
        if dest_location and dest_location.valuation_out_account_id:
            accounts["stock_output"] = dest_location.valuation_out_account_id
        return accounts

    def _get_unit_cost(self):
        """
        If no cost Product is assigned to a work order,
        use the Work Center's Cost Hour.
        """
        unit_cost = super()._get_unit_cost()
        workcenter = self.workcenter_id or self.workorder_id.workcenter_id
        if not unit_cost and workcenter:
            unit_cost = workcenter.costs_hour
        return unit_cost

    @api.depends(
        "analytic_line_ids.amount",
        "parent_id.analytic_line_ids.amount",
        "state",
        "child_ids",
        "product_id.standard_price",
        "actual_stock_move_ids",
        "actual_workorder_ids",
    )
    def _compute_actual_amount(self):
        currency = self.env.company.currency_id
        for item in self:
            if item.state == "cancel" or item.child_ids:
                item.actual_amount = 0.0
            elif item.state == "done":
                return
            elif not item.production_id:
                super(AnalyticTrackingItem, item)._compute_actual_amount()
            else:
                # Specific Actuals calculation on MOs, using current cost
                # instead of the historical cost stored in Anaytic Items
                unit_cost = item.product_id.standard_price
                items = item | item.parent_id
                raw_qty = sum(items.actual_stock_move_ids.mapped("quantity_done"))
                ops_qty = sum(items.actual_workorder_ids.mapped("duration")) / 60
                actual = currency.round(unit_cost * (raw_qty + ops_qty))
                item.actual_amount = actual
        return

    @api.depends(
        "analytic_line_ids.amount",
        "parent_id.analytic_line_ids.amount",
        "planned_amount",
        "accounted_amount",
        "state",
        "child_ids",
    )
    def _compute_actual_amounts(self):
        res = super()._compute_actual_amounts()
        for item in self:
            doing = item.state == "draft"
            remain = max(0, item.requested_amount - item.actual_amount) if doing else 0
            item.remaining_actual_amount = remain
        return res

    def _populate_abcost_tracking_item(self):
        res = super()._populate_abcost_tracking_item()
        to_calculate_with_childs = (self | self.child_ids).filtered("to_calculate")
        for tracking in to_calculate_with_childs:
            cost_rules = tracking.product_id.activity_cost_ids
            # Calculate requested Amount if no ABC an only qty provided
            # or when a ABC tracking (sub)item is created
            if not tracking.requested_amount and not cost_rules:
                factor = tracking.activity_cost_id.factor or 1.0
                unit_cost = tracking._get_unit_cost()
                qty = factor * (
                    tracking.requested_qty or tracking.parent_id.requested_qty
                )
                tracking.requested_amount = qty * unit_cost
        return res
