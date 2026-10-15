# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    propagate_lot_to_byproduct = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")],
        string="Propagate Lot to Byproducts",
        help="Override company setting. Leave empty to use company default.",
    )
