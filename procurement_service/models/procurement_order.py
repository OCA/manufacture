# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _is_procurement_service(self, procurement):
        return procurement.product_id._is_service_buy_make_to_order() or False

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if not res and self._is_procurement_service(procurement):
            return True
        return res

    @api.model
    def _check(self, procurement):
        if self._is_procurement_service(procurement):
            return (procurement.purchase_line_id and
                    procurement.purchase_line_id.order_id.state in
                    ('approved', 'done') or False)
        return super(ProcurementOrder, self)._check(procurement)
