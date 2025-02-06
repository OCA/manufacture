# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class QcInspectionLine(models.Model):
    _name = "qc.inspection.line"
    _inherit = ["qc.inspection.line", "image.mixin"]
