# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    production_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        readonly=True,
        help="Manufacturing Order that produced this lot",
    )
    bom_id = fields.Many2one(
        related="production_id.bom_id",
        readonly=True,
    )
