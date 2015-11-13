# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def _prepare_wc_line(self, wc_use, level=0, factor=1):
        res = super(MrpBom, self)._prepare_wc_line(
            wc_use, level=level, factor=factor)
        wc = wc_use.workcenter_id
        res['pre_cost'] = (
            res.get('time_start', 0.0) * wc.pre_op_product.cost_price)
        res['post_cost'] = (
            res.get('time_stop', 0.0) * wc.post_op_product.cost_price)
        return res
