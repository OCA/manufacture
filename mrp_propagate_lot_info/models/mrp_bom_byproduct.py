# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class MrpBomByproduct(models.Model):
    _inherit = "mrp.bom.byproduct"

    propagate_lot_info = fields.Boolean(
        help="Propagate the configured component lot values to this by-product lot.",
    )
