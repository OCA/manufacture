# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _get_workorder_operations(self, result2, factor, level=0,
                                  routing_id=False):
        res = super(MrpBom, self)._get_workorder_operations(
            result2, factor, level=level, routing_id=routing_id)
        workcenter_obj = self.env['mrp.workcenter']
        for wkr in res:
            wc = workcenter_obj.browse(wkr.get('workcenter_id', False))
            wkr['pre_cost'] = (wkr.get('time_start', 0.0) *
                               wc.pre_op_product.cost_price)
            wkr['post_cost'] = (wkr.get('time_stop', 0.0) *
                                wc.post_op_product.cost_price)
        return result2
