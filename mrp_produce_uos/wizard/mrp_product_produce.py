# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def _default_product_uos_qty(self):
        mrp_production = self.env['mrp.production'].browse(
            self.env.context['active_id'])
        product_qty = self._get_product_qty()
        p_qty = mrp_production.product_qty
        p_uos_qty = mrp_production.product_uos_qty
        product_uos_qty = p_uos_qty * (product_qty / p_qty)
        return product_uos_qty

    product_uos_qty = fields.Float(
        'Select Quantity (UOS)',
        digits=dp.get_precision('Product Unit of Measure'),
        default=_default_product_uos_qty,)

    @api.onchange('product_uos_qty')
    def _onchange_product_uos_qty(self):
        mrp_production = self.env['mrp.production'].browse(
            self.env.context['active_id'])
        p_qty = mrp_production.product_qty
        p_uos_qty = mrp_production.product_uos_qty
        if p_uos_qty != 0:
            self.product_qty = p_qty * (self.product_uos_qty / p_uos_qty)
