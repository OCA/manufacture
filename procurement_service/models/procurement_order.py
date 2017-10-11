# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _is_procurement_service(self):
        return self.product_id._is_service_buy_make_to_order() or False

    @api.multi
    def _assign(self):
        res = super(ProcurementOrder, self)._assign()
        if not res and self._is_procurement_service():
            return True
        return res

    @api.model
    def _check(self):
        if self._is_procurement_service():
            return (self.purchase_line_id and
                    self.purchase_line_id.order_id.state in
                    ('approved', 'done') or False)
        return super(ProcurementOrder, self)._check()

    def _make_po_get_domain(self, partner):
        dom = super(ProcurementOrder, self)._make_po_get_domain(partner)

        # When looking for existing purchase orders,
        # do not consider address, picking type or group: they are not relevant
        # when creating purchase orders for services
        dom = filter(lambda statement: statement[0] not in
                     ('dest_address_id', 'picking_type_id', 'group_id'), dom)
        return dom
