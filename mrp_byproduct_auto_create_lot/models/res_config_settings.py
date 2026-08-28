# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    propagate_lot_to_byproduct = fields.Selection(
        related="company_id.propagate_lot_to_byproduct",
        readonly=False,
    )
