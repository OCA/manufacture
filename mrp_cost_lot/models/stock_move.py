# Copyright 2022 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    total_standard_price = fields.Float(
        string='Total Cost',
        store=True,
        compute='_compute_total_standard_price',
    )

    @api.depends('move_line_ids.total_standard_price')
    def _compute_total_standard_price(self):
        for move in self:
            total_standard_price = 0
            for move_line in move._get_move_lines():
                total_standard_price += move_line.total_standard_price
            move.total_standard_price = total_standard_price

