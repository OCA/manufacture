# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def generate_analytic_line(self):
        """Generate Analytic Lines Manually."""
        for order in self:
            AccountAnalyticLine = self.env["account.analytic.line"].sudo()
            for line in order.move_raw_ids:
                line_vals = {
                    "name": line.product_id.default_code or "",
                    "account_id": order.analytic_account_id.id or False,
                    "ref": order.name,
                    "unit_amount": line.product_uom_qty,
                    "company_id": order.company_id.id,
                    "manufacturing_order_id": order.id,
                    "product_id": line.product_id.id or False,
                    "stock_move_id": line.raw_material_production_id.id,
                }
                analytic_line = AccountAnalyticLine.create(line_vals)
                analytic_line.on_change_unit_amount()
