# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    bom_synchronization_mode = fields.Selection(
        selection=[
            ("warning", "Warning and fix manually"),
            ("auto", "Synchronize automatically"),
        ],
        string="Default BoM Synchronization Mode",
        config_parameter="mrp_bom_synchronization_group.default_synchronization_mode",
        default="warning",
        help="Default synchronization behaviour assigned to new BoM"
        " Synchronization Groups. It can be changed afterwards per group.",
    )
