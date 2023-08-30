# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class QcInspection(models.Model):
    _name = "qc.inspection"
    _inherit = ["qc.inspection", "tier.validation"]
    _state_from = ["waiting"]
    _state_to = ["success", "failed"]

    _tier_validation_manual_config = False

    def action_confirm(self):
        res = super().action_confirm()
        use_validation_on_success_qc = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp.use_validation_on_success_qc")
        )
        if use_validation_on_success_qc:
            for inspection in self:
                inspection.state = "waiting"
        return res
