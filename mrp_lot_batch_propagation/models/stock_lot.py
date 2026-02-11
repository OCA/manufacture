# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    batch_production_id = fields.Many2one(
        "mrp.production",
        help="Production order that created this batch",
        readonly=True,
    )
    batch_bom_id = fields.Many2one(
        "mrp.bom",
        related="batch_production_id.bom_id",
        help="BOM used to produce this batch",
        readonly=True,
    )
