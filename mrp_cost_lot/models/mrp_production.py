# Copyright 2022 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    total_standard_price = fields.Float(
        string='Total Cost',
        store=True,
        compute='_compute_total_standard_price',
    )

    @api.depends('move_raw_ids.total_standard_price')
    def _compute_total_standard_price(self):
        for mrp_order in self:
            total_standard_price = 0
            for move_line in mrp_order.move_raw_ids:
                total_standard_price += move_line.total_standard_price
            mrp_order.total_standard_price = total_standard_price

    def button_mark_done(self):
        res = super().button_mark_done()
        for order in self:
            order.lot_producing_id.standard_price = order.total_standard_price
        return res

