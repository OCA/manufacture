# Copyright 2024 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    qc_duration = fields.Float(
        string="Inspection Duration (hours)",
        help="Time spent on the quality control inspection",
    )
