# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    propagate_lot_to_byproduct = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")],
        string="Propagate Lot to Byproducts",
        default="no",
        required=True,
        help="When set to 'Yes', byproducts receive the same lot name as the "
        "main product.",
    )
