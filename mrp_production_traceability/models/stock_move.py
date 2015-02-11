# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    prod_parent_lot = fields.Many2one('stock.production.lot',
                                      'Parent production lot')
    final_product = fields.Many2one(
        'product.product', string='Final Product', store=True,
        related='production_id.product_id', help='Production Final Product')
