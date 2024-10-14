# Copyright 2024 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    qc_inspection_id = fields.Many2one(
        "qc.inspection",
        string="Related QC Inspection",
        help="The quality control inspection related to this timesheet entry.",
    )
