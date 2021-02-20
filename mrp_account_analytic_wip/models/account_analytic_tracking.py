# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticTrackingItem(models.Model):
    _inherit = "account.analytic.tracking.item"

    stock_move_id = fields.Many2one(
        "stock.move", string="Stock Move", ondelete="cascade"
    )
    workorder_id = fields.Many2one(
        "mrp.workorder", string="Work Order", ondelete="cascade"
    )

    @api.depends("stock_move_id.product_id", "workorder_id.display_name")
    def _compute_name(self):
        super()._compute_name()
        for tracking in self.filtered("stock_move_id"):
            move = tracking.stock_move_id
            tracking.name = "{} / {}".format(
                move.raw_material_production_id.name,
                move.product_id.display_name,
            )
        for tracking in self.filtered("workorder_id"):
            workorder = tracking.workorder_id
            tracking.name = workorder.display_name

    def _get_accounting_data_for_valuation(self):
        accounts = super()._get_accounting_data_for_valuation()
        stock_move = self.stock_move_id
        if stock_move:
            # Similar logic to StockMove._get_accounting_data_for_valuation()
            # to get input/output accounts from the Production location
            input_account = stock_move.location_id.valuation_out_account_id
            if input_account:
                accounts["stock_input"] = input_account
            output_account = stock_move.location_dest_id.valuation_in_account_id
            if output_account:
                accounts["stock_output"] = output_account
        return accounts

    def _get_journal_entries_done(self, wip_amount=0.0, variance_amount=0.0):
        """
        When an MO is completed, closing WIP for raw materials
        is different because is needs to compensate for the
        stock valuation JEs generated bu the MRP App
        """
        entries = super()._get_journal_entries_done(wip_amount, variance_amount)
        if self.stock_move_id:
            entries = {
                "stock_valuation": wip_amount + variance_amount,
                "stock_wip": -wip_amount,
                "stock_output": -variance_amount,
            }
        return entries
