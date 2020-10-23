# -*- coding: utf-8 -*-
# Copyright 2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare, float_is_zero


class MrpProduction(models.TransientModel):
    _inherit = 'mrp.product.produce'

    auto_fill_done = fields.Boolean(readonly=True)

    def action_consume_line_auto_fill(self):
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self.consume_line_ids.filtered(
                lambda x: x.product_id.tracking in ('serial', 'lot')):
            if (
                    float_compare(
                        line.quantity, 0, precision_digits=prec) > 0 and
                    float_is_zero(
                        line.quantity_done, precision_digits=prec)):
                line.write({'quantity_done': line.quantity})
        self.write({'auto_fill_done': True})
        action = self.env.ref('mrp.act_mrp_product_produce').read([])[0]
        action['res_id'] = self.id
        return action
