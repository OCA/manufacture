# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MRPWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    def _prepare_mrp_workorder_analytic_item(self):
        """
        Prepare additional values for Analytic Items created.
        For compatibility with analytic_activity_cost
        """
        self.ensure_one()
        return {
            "name": "{} / {}".format(self.production_id.name, self.name),
            "account_id": self.production_id.analytic_account_id.id,
            "date": fields.Date.today(),
            "company_id": self.company_id.id,
            "manufacturing_order_id": self.production_id.id,
            "workorder_id": self.id,
            "unit_amount": self.duration / 60,  # convert minutes to hours
            "amount": -self.duration / 60 * self.workcenter_id.costs_hour,
        }

    def generate_mrp_work_analytic_line(self):
        """Generate Analytic Lines"""
        AnalyticLine = self.env["account.analytic.line"].sudo()
        workorders = self.filtered("production_id.analytic_account_id")
        existing_items = workorders and AnalyticLine.search(
            [("workorder_id", "in", self.ids)]
        )
        for workorder in workorders:
            line_vals = self._prepare_mrp_workorder_analytic_item()
            analytic_lines = existing_items.filtered(
                lambda x: x.workorder_id == workorder
            )
            if analytic_lines:
                for analytic_line in analytic_lines:
                    analytic_line.write(line_vals)
                    analytic_line.on_change_unit_amount()
            else:
                analytic_line = AnalyticLine.create(line_vals)
                analytic_line.on_change_unit_amount()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("duration"):
            res.generate_mrp_work_analytic_line()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("duration"):
            self.generate_mrp_work_analytic_line()
        return res
