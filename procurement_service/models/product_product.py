# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _is_service_buy_make_to_order(self):
        for product in self:
            if (product.type == 'service' and len(product.route_ids) == 2 and
                self.env.ref('stock.route_warehouse0_mto').id in
                product.route_ids.ids and
                self.env.ref('purchase.route_warehouse0_buy').id in
                    product.route_ids.ids):
                return True
        return False

    @api.multi
    def need_procurement(self):
        for product in self:
            if product._is_service_buy_make_to_order():
                return True
        return super(ProductProduct, self).need_procurement()
