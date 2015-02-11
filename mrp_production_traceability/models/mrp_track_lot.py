# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class MrpTrackLot(models.Model):
    _name = "mrp.track.lot"

    component = fields.Many2one('product.product', 'Component')
    component_lot = fields.Many2one('stock.production.lot', 'Component Lot')
    product = fields.Many2one('product.product', 'Final Product')
    product_lot = fields.Many2one('stock.production.lot', 'Final Product Lot')
    production = fields.Many2one('mrp.production', 'Production')
    st_move = fields.Many2one('stock.move', 'Stock Move')
