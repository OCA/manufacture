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
        for item in self.filtered("workorder_id"):
            item.name = "{} / {}".format(
                item.analytic_id.display_name, item.workorder_id.display_name
            )

    @api.depends("manual_planned_amount", "workorder_id")
    def _compute_planned_amount(self):
        for item in self:
            item.planned_amount = (
                item.manual_planned_amount or item.workorder_id.tracked_planned_amount
            )
