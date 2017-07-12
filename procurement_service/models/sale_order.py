# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        rule_obj = self.env['procurement.rule']
        vals = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        if line.product_id._is_service_buy_make_to_order():
            cond = [('warehouse_id', '=', order.warehouse_id.id),
                    ('route_id', '=',
                     self.env.ref('purchase.route_warehouse0_buy').id),
                    ('action', '=', 'buy')]
            rule = rule_obj.search(cond, limit=1)
            vals['rule_id'] = rule.id or False
        return vals
