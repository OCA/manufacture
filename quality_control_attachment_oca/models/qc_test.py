# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcTest(models.Model):
    _inherit = "qc.test"

    is_required_attachment = fields.Boolean(
        string="Required attachment",
        default=False,
        help="Defines whether at least one attachment should be added to the inspection",
    )
