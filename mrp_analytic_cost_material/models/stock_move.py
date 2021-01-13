# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_mrp_raw_material_analytic_line(self):
        self.ensure_one()
        move = self
        mrp_order = move.raw_material_production_id
        return {
            "date": move.date,
            "name": "{} / {}".format(mrp_order.name, move.product_id.display_name),
            "ref": mrp_order.name,
            "account_id": mrp_order.analytic_account_id.id,
            "manufacturing_order_id": mrp_order.id,
            "company_id": mrp_order.company_id.id,
            "stock_move_id": move.id,
            "product_id": move.product_id.id,
            "unit_amount": move.quantity_done,
        }

    def generate_mrp_raw_analytic_line(self):
        """Generate Analytic Lines"""
        # FIXME: consumed products coming from child MOs
        # should not generate Analytic Items, to avoid duplicating costs!
        AnalyticLine = self.env["account.analytic.line"].sudo()
        existing_items = AnalyticLine.search([("stock_move_id", "in", self.ids)])
        for move in self.filtered("raw_material_production_id.analytic_account_id"):
            line_vals = move._prepare_mrp_raw_material_analytic_line()
            if move in existing_items.mapped("stock_move_id"):
                analytic_line = existing_items.filtered(
                    lambda x: x.stock_move_id == move
                )
                analytic_line.write(line_vals)
                analytic_line.on_change_unit_amount()
            elif line_vals.get("unit_amount"):
                analytic_line = AnalyticLine.create(line_vals)
                analytic_line.on_change_unit_amount()

    def _quantity_done_set(self):
        """ When material is consumed, generate Analytic Items """
        super()._quantity_done_set()
        self.generate_mrp_raw_analytic_line()
