# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticTrackingItem(models.Model):
    _inherit = "account.analytic.tracking.item"

    workorder_id = fields.Many2one(
        "mrp.workorder", string="Work Order", ondelete="restrict"
    )

    def _compute_name(self):
        super()._compute_name()
        for tracking in self.filtered("workorder_id"):
            workorder = tracking.workorder_id
            tracking.name = workorder.display_name

    @api.depends("manual_planned_amount", "workorder_id")
    def _compute_planned_amount(self):
        super()._compute_planned_amount()
        for tracking in self.filtered("workorder_id"):
            workorder = tracking.workorder_id
            hours = workorder.duration_expected / 60
            unit_cost = workorder.workcenter_id.costs_hour
            tracking.planned_amount += hours * unit_cost
