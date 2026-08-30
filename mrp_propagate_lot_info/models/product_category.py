# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    mrp_propagate_lot_profile_id = fields.Many2one(
        comodel_name="mrp.lot.info.propagation.profile",
        string="MRP Lot Propagation Profile",
        help=(
            "Default lot propagation profile for consumed components in "
            "manufacturing."
        ),
    )
