# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_partial_kit_delivery = fields.Boolean(
        default=True,
        help="If not set, and this product is delivered with a BoM of type "
        "kit, partial deliveries of the components won't be allowed.",
    )
    display_allow_partial_kit_delivery = fields.Boolean(
        compute="_compute_display_allow_partial_kit_delivery",
    )

    @api.depends("bom_count", "type")
    def _compute_display_allow_partial_kit_delivery(self):
        for record in self:
            record.display_allow_partial_kit_delivery = (
                record.bom_count > 0 and record.type in ["consu", "product"]
            )
