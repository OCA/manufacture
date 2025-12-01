# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    quality_inspection_report_id = fields.Many2one(
        "ir.actions.report",
        string="Inspection Report for Signature",
        domain="[('model', '=', 'qc.inspection'), ('report_type', '=', 'qweb-pdf')]",
        config_parameter="quality_control_sign_oca.quality_inspection_report_id",
    )
