# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _prepare_material_analytic_line(self):
        self.ensure_one()
        order = self.raw_material_production_id
        return {
            "name": self.product_id.default_code or "",
            "account_id": order.analytic_account_id.id or False,
            "ref": order.name,
            "unit_amount": self.product_uom_qty,
            "company_id": order.company_id.id,
            "manufacturing_order_id": order.id,
            "product_id": self.product_id.id or False,
            "stock_move_id": self.id,
        }

    def generate_analytic_line(self):
        """Generate Analytic Lines Manually."""
        # FIXME: this is a placeholder for final logic
        # TODO: when should Analytic Items generation be triggered?
        # TODO: what to do if prevous items were already generated?
        AnalyticLine = self.env["account.analytic.line"].sudo()
        order_raw_moves = self.mapped("move_raw_ids")
        existing_items = AnalyticLine.search(
            [("stock_move_id ", "in", order_raw_moves.ids)]
        )
        for order in self.filtered("analytic_account_id"):
            for line in order.move_raw_ids:
                line_vals = line._prepare_material_analytic_line()
                if line in existing_items:
                    analytic_line = existing_items.filter(
                        lambda x: x.stock_move_id == line
                    )
                    analytic_line.write(line_vals)
                else:
                    analytic_line = AnalyticLine.create(line_vals)
                analytic_line.on_change_unit_amount()
