# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_kit_inventory = fields.Boolean(
        default=False,
        help="If set, users will be able to create inventory adjustments for kits,"
        "same as standard behavior. Leave unchecked to keep the restriction",
    )
