# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    def _prepare_mrp_workorder_analytic_item(self, duration):
        """
        Prepare additional values for Analytic Items created.
        For compatibility with analytic_activity_cost
        """
        self.ensure_one()
        duration_hours = duration / 60
        amount = duration_hours * self.workcenter_id.costs_hour
        return {
            "name": "{} / {}".format(self.production_id.name, self.workorder_id.name),
            "account_id": self.production_id.analytic_account_id.id,
            "date": fields.Date.today(),
            "company_id": self.company_id.id,
            "manufacturing_order_id": self.production_id.id,
            "workorder_id": self.workorder_id.id,
            "unit_amount": duration_hours,
            "amount": -amount,
        }

    def generate_mrp_work_analytic_line(self, duration):
        if duration and self.production_id.analytic_account_id:
            line_vals = self._prepare_mrp_workorder_analytic_item(duration=duration)
            AnalyticLine = self.env["account.analytic.line"].sudo()
            analytic_line = AnalyticLine.create(line_vals)
            analytic_line.on_change_unit_amount()

    @api.model
    def create(self, vals):
        timelog = super().create(vals)
        if timelog.duration:
            timelog.generate_mrp_work_analytic_line(duration=timelog.duration)
        return timelog

    def write(self, vals):
        for timelog in self:
            old_duration = timelog.duration
            super(MrpWorkcenterProductivity, timelog).write(vals)
            new_duration = timelog.duration
            diff_duration = round(new_duration - old_duration, 2)
            if diff_duration:
                timelog.generate_mrp_work_analytic_line(duration=diff_duration)
        return True

    def unlink(self):
        # Setting time spent to zero will remove Time Logs
        for timelog in self:
            timelog.generate_mrp_work_analytic_line(duration=-timelog.duration)
        return super().unlink()
