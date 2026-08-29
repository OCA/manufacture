# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_same_product_component_finish = fields.Boolean(
        related="company_id.allow_same_product_component_finish",
        string="Allow Same Product for Component and Finish",
        readonly=False,
    )
