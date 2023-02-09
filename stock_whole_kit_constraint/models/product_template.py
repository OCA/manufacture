# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_partial_kit_delivery = fields.Boolean(
        default=True,
        help="If not set, and this product is delivered with a BoM of type "
        "kit, partial deliveries of the components won't be allowed.",
    )
