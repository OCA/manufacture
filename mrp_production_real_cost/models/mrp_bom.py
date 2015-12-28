# -*- coding: utf-8 -*-
# © 2014-2015 Avanzosc
# © 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def _prepare_wc_line(self, wc_use, level=0, factor=1):
        res = super(MrpBom, self)._prepare_wc_line(
            wc_use, level=level, factor=factor)
        wc = wc_use.workcenter_id
        res['pre_cost'] = (
            res.get('time_start', 0.0) * wc.pre_op_product.standard_price)
        res['post_cost'] = (
            res.get('time_stop', 0.0) * wc.post_op_product.standard_price)
        return res
