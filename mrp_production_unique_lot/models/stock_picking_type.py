# Copyright 2025 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    force_production_lot_uniqueness = fields.Boolean(
        help="If checked, each Manufacturing Order (MO) will have a unique lot "
        "number for its finished products. Therefore, lot numbers that have "
        "already been used in an MO cannot be reused.",
    )
