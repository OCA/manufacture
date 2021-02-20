# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    analytic_tracking_item_ids = fields.Many2many(
        "account.analytic.tracking.item",
        string="Tracking Items",
        compute="_compute_analytic_tracking_item",
    )
    analytic_tracking_item_count = fields.Integer(
        "WIP Item Count", compute="_compute_analytic_tracking_item"
    )
    analytic_tracking_item_amount = fields.Float(
        "WIP Actual Amount", compute="_compute_analytic_tracking_item"
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    @api.depends(
        "move_raw_ids.state",
        "move_raw_ids.quantity_done",
        "move_finished_ids.state",
        "workorder_ids",
        "workorder_ids.state",
        "product_qty",
        "qty_producing",
    )
    def _compute_state(self):
        """
        Now aving all raw material moves done is not enough to set the MO as done.
        Should only set as done if the finished moves are all done.
        """
        super()._compute_state()
        for production in self:
            all_finished_moves_done = all(
                move.state == "done" for move in production.move_finished_ids
            )
            all_workorders_done = not production.workorder_ids or all(
                wo.state in ("done", "cancel") for wo in production.workorder_ids
            )
            if production.state == "done" and not all_finished_moves_done:
                if all_workorders_done:
                    production.state = "to_close"
                else:
                    production.state = "progress"

    def _get_tracking_items(self):
        """
        Returns a recordset with the related Ttacking Items
        """
        return (
            self.mapped("move_raw_ids.analytic_tracking_item_id")
            | self.mapped("workorder_ids.analytic_tracking_item_id")
            | self.mapped("workorder_ids.analytic_tracking_item_id.child_ids")
        )

    @api.depends(
        "move_raw_ids.analytic_tracking_item_id",
        "workorder_ids.analytic_tracking_item_id",
    )
    def _compute_analytic_tracking_item(self):
        for mo in self:
            mo.analytic_tracking_item_ids = mo._get_tracking_items()
            mo.analytic_tracking_item_count = len(mo.analytic_tracking_item_ids)
            mo.analytic_tracking_item_amount = sum(
                mo.analytic_tracking_item_ids.mapped("actual_amount")
            )

    def _post_inventory(self, cancel_backorder=False):
        """
        Does MO closing.
        Ensure all done raw material moves are set
        on the consumed lines field, for correct traceability (and proper unbuild).

        The Odoo code will post all material to the "Input" (WIP) account.
        So the clear WIP method may need to convert some of this WIP into Variances.
        """
        # _post_inventory will post missing raw material WIP and the final product
        super()._post_inventory(cancel_backorder=cancel_backorder)
        for order in self:
            # Correct consume_line_ids, that otherwise will miss
            # the early consumed raw materials
            moves_done = order.move_raw_ids.filtered(lambda x: x.state == "done")
            consume_move_lines = moves_done.mapped("move_line_ids")
            order.move_finished_ids.move_line_ids.consume_line_ids = [
                (6, 0, consume_move_lines.ids)
            ]
        return True

    def action_post_inventory_wip(self, cancel_backorder=False):
        """
        A variation of _post_inventory that allows consuming raw materials
        during MO execution, rather than only at MO completion.
        Triggered by button click, not automatic on raw material consumption.
        TODO: have an action available on MO list view
        """
        for order in self:
            moves_all = order.move_raw_ids
            for move in moves_all:
                move.product_uom_qty = move.quantity_done
            # Raw Material Consumption, closely following _post_inventory()
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == "done")
            moves_to_do = order.move_raw_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
            # MRP do not merge move, catch the result of _action_done in order
            # to get extra moves.
            moves_to_do = moves_to_do._action_done()
            moves_to_do = (
                order.move_raw_ids.filtered(lambda x: x.state == "done")
                - moves_not_to_do
            )
            order._cal_price(moves_to_do)
            order.action_assign()
            consume_move_lines = moves_to_do.mapped("move_line_ids")
            order.move_finished_ids.move_line_ids.consume_line_ids |= consume_move_lines

            # update posted and to post columns on Tracking Items!
            for tracking in moves_all.mapped("analytic_tracking_item_id"):
                tracking.accounted_amount = tracking.actual_amount

            # Post Work Order WIP
            workorders_tracking = order.workorder_ids.mapped(
                "analytic_tracking_item_id"
            )
            workorders_tracking |= workorders_tracking.child_ids
            tracking_todo = workorders_tracking.filtered("pending_amount")
            tracking_todo.process_wip_and_variance()

        return True

    def _prepare_clear_wip_account_line(self, account, amount):
        # Note: do not set analytic_account_id,
        # as that triggers a (repeated) Analytic Item
        return {
            "ref": _("%s - Clear WIP") % (self.display_name),
            "product_id": self.product_id.id,
            "product_uom_id": self.product_id.uom_id.id,
            "account_id": account.id,
            "debit": amount if amount > 0.0 else 0.0,
            "credit": -amount if amount < 0.0 else 0.0,
            "analytic_account_id": self.analytic_account_id.id,
        }

    def clear_wip_final(self):
        """
        Add final Clear WIP JE journal entry.
        Looks up the WIP account balance and clears it using the Variance account.

        - WIP Account is the Production Location Input Account.
        - Variance Account is the Production Location Variance account.
        """
        for prod in self:
            # Find WIP and Variance Accounts
            prod_location = prod.production_location_id
            # acc_wip_prod = prod_location.valuation_in_account_id
            acc_var = prod_location.valuation_variance_account_id
            acc_clear = prod_location.valuation_clear_account_id

            if not (acc_clear and acc_var):
                _logger.debug(
                    "No Clear or Variance account found for MO %s", prod.display_name
                )
                continue

            # Find the balance of the WIP account...
            # Issue: Finished product has no related account moves!
            stock_moves = prod.move_raw_ids | prod.move_finished_ids
            stock_account_moves = (
                stock_moves.account_move_ids
                | prod.analytic_tracking_item_ids.account_move_ids
            )
            wip_items = stock_account_moves.line_ids.filtered("is_wip")

            # ... clear each of the WIP accounts
            move_lines = []
            accounts_wip = wip_items.mapped("account_id")
            for acc_wip in accounts_wip:
                wip_acc_items = wip_items.filtered(lambda x: x.account_id == acc_wip)
                wip_acc_bal = sum(wip_acc_items.mapped("balance"))
                # Should we do separate Journal Entry for each WIP account?
                if wip_acc_bal:
                    move_lines.extend(
                        [
                            prod._prepare_clear_wip_account_line(acc_wip, -wip_acc_bal),
                            prod._prepare_clear_wip_account_line(
                                acc_clear, +wip_acc_bal
                            ),
                        ]
                    )

            # The final product valuation move is used as a template for the header
            # Alternative solution would be to add a prepare header method
            final_prod_move = prod.move_finished_ids.filtered(
                lambda x: x.product_id == prod.product_id
            )
            final_acc_move = final_prod_move.account_move_ids[:1]
            if move_lines and final_acc_move:
                wip_move = final_acc_move.copy(
                    {
                        "ref": _("%s Clear WIP") % (prod.name),
                        "line_ids": [(0, 0, x) for x in move_lines or [] if x],
                    }
                )
                wip_move._post()

    def _cron_process_wip_and_variance(self):
        items = self.env["mrp.variance"].search(
            [("state", "in", ["progress", "to_close"])]
        )
        items.action_post_inventory_wip()
        super()._cron_process_wip_and_variance()

    def action_view_analytic_tracking_items(self):
        self.ensure_one()
        return {
            "res_model": "account.analytic.tracking.item",
            "type": "ir.actions.act_window",
            "name": _("%s Tracking Items") % self.name,
            "domain": [("id", "in", self._get_tracking_items().ids)],
            "view_mode": "tree,form",
        }

    def action_confirm(self):
        """
        On MO Confirm, save the planned amount on the tracking item.
        Note that in some cases, the Analytic Account might be set
        just after MO confirmation.
        """
        res = super().action_confirm()
        self.mapped("move_raw_ids").populate_tracking_items(set_planned=True)
        self.mapped("workorder_ids").populate_tracking_items(set_planned=True)
        return res

    def button_mark_done(self):
        # Post all pending WIP and then generate MO close JEs
        self.action_post_inventory_wip()
        # Run finished product valuation (no raw materials to valuate now)
        res = super().button_mark_done()
        mfg_done = self.filtered(lambda x: x.state == "done")
        if mfg_done:
            tracking = mfg_done._get_tracking_items()
            # Ensure all pending WIP is posted
            tracking.process_wip_and_variance(close=True)
            # Operations - clear WIP
            tracking.clear_wip_journal_entries()
            # Raw Material - clear final WIP and post Variances
            mfg_done.clear_wip_final()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self._get_tracking_items().action_cancel()
        return res

    @api.model
    def create(self, vals):
        new = super().create(vals)
        # Do not copy Tracking Items wjen duplicating an MO
        to_fix = new.move_raw_ids.filtered("analytic_tracking_item_id")
        to_fix.write({"analytic_tracking_item_id": None})
        return new

    def write(self, vals):
        """
        When setting the Analytic account,
        generate tracking items.

        On MTO, the Analytic Account might be set after the action_confirm(),
        so the planned amount needs to be set here.

        TODO: in what cases the planned amounts update should be prevented?
        """
        super().write(vals)
        if "analytic_account_id" in vals:
            confirmed_mos = self.filtered(lambda x: x.state == "confirmed")
            confirmed_mos.move_raw_ids.populate_tracking_items()
            confirmed_mos.workorder_ids.populate_tracking_items()
        return True

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        vals = super()._get_move_raw_values(
            product_id, product_uom_qty, product_uom, operation_id, bom_line
        )
        vals.update({"qty_planned": vals.get("product_uom_qty")})
        return vals

    def _create_workorder(self):
        super()._create_workorder()
        for production in self:
            for workorder in production.workorder_ids:
                workorder.duration_planned = workorder.duration_expected
