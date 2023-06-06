# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    def _prepare_mrp_workorder_analytic_item(self):
        """
        Prepare additional values for Analytic Items created.
        For compatibility with analytic_activity_cost
        """
        self.ensure_one()
        return {
            "name": "{} / {}".format(self.production_id.name, self.workorder_id.name),
            "account_id": self.production_id.analytic_account_id.id,
            "date": fields.Date.today(),
            "company_id": self.company_id.id,
            "manufacturing_order_id": self.production_id.id,
            "workorder_id": self.workorder_id.id,
            "unit_amount": self.duration / 60,  # convert minutes to hours
            "amount": -self.duration / 60 * self.workcenter_id.costs_hour,
        }

    def generate_mrp_work_analytic_line(self):
        AnalyticLine = self.env["account.analytic.line"].sudo()
        for timelog in self:
            line_vals = timelog._prepare_mrp_workorder_analytic_item()
            analytic_line = AnalyticLine.create(line_vals)
            analytic_line.on_change_unit_amount()

    @api.model
    def create(self, vals):
        timelog = super().create(vals)
        if vals.get("date_end"):
            timelog.generate_mrp_work_analytic_line()
        return timelog

    def write(self, vals):
        res = super().write(vals)
        if vals.get("date_end"):
            self.generate_mrp_work_analytic_line()
        return res
