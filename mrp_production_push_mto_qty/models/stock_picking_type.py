# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    push_mto_qty_to_dest_moves = fields.Boolean(
        string="Push Produced Quantity to MTO Moves",
        help="When a manufacturing order is done, update the demand of the "
        "ensuing moves (e.g. the delivery) according to the quantity produced:\n"
        " * producing more increases the demand,\n"
        " * producing less without backorder decreases the demand,\n"
        " * producing less with a backorder keeps the demand unchanged.\n"
        "Cancelling a backorder manufacturing order also decreases the demand "
        "by its remaining quantity.",
    )
