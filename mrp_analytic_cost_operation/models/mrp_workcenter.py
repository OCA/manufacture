# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MRPWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    analytic_product_id = fields.Many2one(
        "product.product",
        string="Cost Type",
    )


class MRPWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def _prepare_mrp_workorder_analytic_item(self):
        self.ensure_one()
        return {
            "name": "{} / {}".format(self.production_id.name, self.name),
            "account_id": self.production_id.analytic_account_id.id,
            "date": self.date_start,
            "company_id": self.company_id.id,
            "manufacturing_order_id": self.production_id.id,
            "product_id": self.workcenter_id.analytic_product_id.id,
            "unit_amount": self.duration,
            "workorder_id": self.id,
        }

    def write(self, vals):
        res = super().write(vals)
        if vals.get("duration"):
            AnalyticLine = self.env["account.analytic.line"].sudo()
            workorders = self.filtered("workcenter_id.analytic_product_id")
            existing_items = workorders and AnalyticLine.search(
                [("workorder_id", "=", self.ids)]
            )
            for workorder in workorders:
                analytic_line = existing_items.filter(
                    lambda x: x.workorder_id == workorder
                )
                line_vals = self._prepare_mrp_workorder_analytic_item()
                if analytic_line:
                    analytic_line.write(line_vals)
                else:
                    analytic_line = AnalyticLine.create(line_vals)
                analytic_line.on_change_unit_amount()
        return res
