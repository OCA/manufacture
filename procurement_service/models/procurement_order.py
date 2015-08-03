# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if procurement.product_id.type == 'service':
            rule_id = self._find_suitable_rule(procurement)
            if rule_id:
                procurement.rule_id = rule_id
            res = bool(rule_id)
        return res
