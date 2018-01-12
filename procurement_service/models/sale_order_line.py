# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_procurement_create(self):
        # When creating procurements, create procurements of services
        # after ordinary procurements: in this way we keep their
        # characteristics in the resulting purchase order
        self = self.sorted(
            key=lambda line: line.product_id._service_need_procurement())
        return super(SaleOrderLine, self)._action_procurement_create()

    @api.model
    def _prepare_order_line_procurement(self, group_id=False):
        rule_obj = self.env['procurement.rule']
        vals = super(SaleOrderLine, self).\
            _prepare_order_line_procurement(group_id=group_id)
        if self.product_id._service_need_procurement():
            cond = [('warehouse_id', '=', self.order_id.warehouse_id.id),
                    ('route_id', '=',
                     self.env.ref('purchase.route_warehouse0_buy').id),
                    ('action', '=', 'buy')]
            rule = rule_obj.search(cond, limit=1)
            vals['rule_id'] = rule.id or False
        return vals
