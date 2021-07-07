# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_mrp_raw_material_analytic_line(self):
        """
        Prepare additional values for Analytic Items created.
        """
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
        """
        Generate Analytic Lines.
        One Analytic Item for each Stock Move line.
        If the Stock Move is updated, the existing Analytic Item is updated.
        """
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

    def write(self, vals):
        """ When material is consumed, generate Analytic Items """
        res = super().write(vals)
        if vals.get("quantity_done"):
            self.generate_mrp_raw_analytic_line()
        return res

    @api.model
    def create(self, vals):
        qty_done = vals.get("quantity_done")
        res = super().create(vals)
        if qty_done:
            res.generate_mrp_raw_analytic_line()
        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        qty_done = vals.get("qty_done")
        res = super().write(vals)
        if qty_done:
            self.mapped("move_id").generate_mrp_raw_analytic_line()
        return res

    @api.model
    def create(self, vals):
        qty_done = vals.get("qty_done")
        res = super().create(vals)
        if qty_done:
            res.mapped("move_id").generate_mrp_raw_analytic_line()
        return res
