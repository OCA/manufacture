# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBomByproduct(models.Model):
    _inherit = "mrp.bom.byproduct"

    inherit_lot = fields.Boolean(
        help="Apply the same lot generated on the production to this by-product"
    )
