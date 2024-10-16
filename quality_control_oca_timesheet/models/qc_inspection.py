# Copyright 2024 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    timesheet_ids = fields.One2many(
        "account.analytic.line",
        "qc_inspection_id",
        string="Timesheets",
    )

    timesheet_total_hours = fields.Float(
        string="Total Hours",
        compute="_compute_timesheet_total_hours",
        store=True,
        help="Total hours spent on this quality control inspection.",
    )

    @api.depends("timesheet_ids.unit_amount")
    def _compute_timesheet_total_hours(self):
        for inspection in self:
            inspection.timesheet_total_hours = sum(
                inspection.timesheet_ids.mapped("unit_amount")
            )
