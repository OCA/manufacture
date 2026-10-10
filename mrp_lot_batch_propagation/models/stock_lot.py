# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    batch_production_ids = fields.Many2many(
        "mrp.production",
        help="Production orders that created this batch",
        readonly=True,
    )
    batch_bom_ids = fields.Many2many(
        "mrp.bom",
        help="BOMs used to produce this batch",
        readonly=True,
    )
