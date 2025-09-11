# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcInspectionType(models.Model):
    _name = "qc.inspection.type"
    _description = "Quality control inspection type"

    name = fields.Char()
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
    )
