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
            result2, factor, level, routing_id)
        for work_order in res:
            seq = work_order['sequence'] - level
            rl = self._get_routing_line_from_workorder(
                routing_id, seq, work_order['workcenter_id'],
                work_order['name'])
            work_order['init_without_material'] = rl.init_without_material
        return res
