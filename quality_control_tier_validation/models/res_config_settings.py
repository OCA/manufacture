# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_validation_on_success_qc = fields.Boolean(
        string="Tier Validation on success quality control",
        config_parameter="mrp.use_validation_on_success_qc",
    )
