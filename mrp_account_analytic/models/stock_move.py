# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_mrp_raw_material_analytic_line(self, qty):
        """
        Prepare additional values for Analytic Items created.
        """
        self.ensure_one()
        mrp_order = self.raw_material_production_id
        return {
            "date": self.date,
            "name": "{} / {}".format(mrp_order.name, self.product_id.display_name),
            "ref": mrp_order.name,
            "account_id": mrp_order.analytic_account_id.id,
            "manufacturing_order_id": mrp_order.id,
            "company_id": mrp_order.company_id.id,
            "stock_move_id": self.id,
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "unit_amount": qty,
        }

    def generate_mrp_raw_analytic_line(self, qty):
        """
        Generate Analytic Lines for each consumption
        """
        if qty and self.raw_material_production_id.analytic_account_id:
            line_vals = self._prepare_mrp_raw_material_analytic_line(qty=qty)
            AnalyticLine = self.env["account.analytic.line"].sudo()
            analytic_line = AnalyticLine.create(line_vals)
            analytic_line.on_change_unit_amount()


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, vals):
        qty_done = vals.get("qty_done")
        res = super().create(vals)
        res.move_id.generate_mrp_raw_analytic_line(qty=qty_done)
        return res

    def write(self, vals):
        for move_line in self:
            old_qty = move_line.qty_done
            super(StockMoveLine, move_line).write(vals)
            new_qty = move_line.qty_done
            diff_qty = new_qty - old_qty
            if diff_qty:
                move_line.move_id.generate_mrp_raw_analytic_line(qty=diff_qty)
        return True

    def unlink(self):
        for move_line in self:
            move_line.move_id.generate_mrp_raw_analytic_line(qty=-move_line.qty_done)
        return super().unlink()
