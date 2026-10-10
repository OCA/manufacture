from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mrp_serial_matrix_allow_exceptions = fields.Boolean(
        "Allow manufacturing exceptions",
        config_parameter="mrp_production_serial_matrix.mrp_serial_matrix_allow_exceptions",
    )
