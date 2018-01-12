# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _service_need_procurement(self):
        """Override to choose when service products should generate
        procurements"""
        for product in self:
            if (product.type == 'service' and len(product.route_ids) == 2 and
                self.env.ref('stock.route_warehouse0_mto').id in
                product.route_ids.ids and
                self.env.ref('purchase.route_warehouse0_buy').id in
                    product.route_ids.ids):
                return True
        return False

    @api.multi
    def _need_procurement(self):
        for product in self:
            if product.type == 'service' and self._service_need_procurement():
                return True
        return super(ProductProduct, self)._need_procurement()
