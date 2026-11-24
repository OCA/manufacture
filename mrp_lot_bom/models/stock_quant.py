# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    bom_id = fields.Many2one(
        related="lot_id.bom_id",
        store=True,
        index=True,
    )
