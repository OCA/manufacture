# Copyright 2022 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_standard_price = fields.Float(
        string="Lot Cost Price",
        related="lot_id.standard_price",
    )
    total_standard_price = fields.Float(
        string='Total',
        store=True,
        compute='_compute_total_standard_price',
    )

    @api.depends('lot_standard_price', 'qty_done')
    def _compute_total_standard_price(self):
        for line in self:
            line.total_standard_price = line.lot_standard_price * line.qty_done
