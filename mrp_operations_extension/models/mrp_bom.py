# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
import math


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        routing_id = bom.routing_id.id or routing_id
        result, result2 = super(MrpBom, self)._bom_explode(
            bom, product, factor, properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom)
        result2 = self._get_workorder_operations(
            result2, factor=factor, level=level, routing_id=routing_id)
        return result, result2

    def _get_routing_line_from_workorder(self, routing_id, seq, workcenter_id,
                                         wo_name):
        """ Returns first routing line from a given data if found
        @param routing_id: Routing id
        @param seq: workorder sequence
        @param workcenter_id: Workcenter id
        @return: wo_name = Workorder name
        """
        routing_line_obj = self.env['mrp.routing.workcenter']
        domain = [('routing_id', '=', routing_id), ('sequence', '=', seq),
                  ('workcenter_id', '=', workcenter_id)]
        routing_lines = routing_line_obj.search(domain)
        for rl in routing_lines:
            if rl.name in wo_name:
                return rl
        return routing_line_obj

    def _get_workorder_operations(self, result2, factor, level=0,
                                  routing_id=False):
        for work_order in result2:
            if (work_order['sequence'] < level or
                    work_order.get('routing_wc_line')):
                continue
            seq = work_order['sequence'] - level
            rl = self._get_routing_line_from_workorder(
                routing_id, seq, work_order['workcenter_id'],
                work_order['name'])
            cycle = rl.cycle_nbr and int(math.ceil(factor / rl.cycle_nbr)) or 0
            hour = rl.hour_nbr * cycle
            default_wc_line = rl.op_wc_lines.filtered(lambda r: r.default)
            work_order['cycle'] = cycle
            work_order['hour'] = hour
            work_order['time_start'] = default_wc_line.time_start or 0.0
            work_order['time_stop'] = default_wc_line.time_stop or 0.0
            work_order['routing_wc_line'] = rl.id
            work_order['do_production'] = rl.do_production
        return result2

    @api.multi
    @api.onchange('routing_id')
    def onchange_routing_id(self):
        for line in self.bom_line_ids:
            line.operation = (self.routing_id.workcenter_lines and
                              self.routing_id.workcenter_lines[0])
        if self.routing_id:
            return {'warning': {
                    'title': _('Changing Routing'),
                    'message': _("Changing routing will cause to change the"
                                 " operation in which each component will be"
                                 " consumed, by default it is set the first"
                                 " one of the routing")
                    }}
        return {}


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    operation = fields.Many2one(
        comodel_name='mrp.routing.workcenter', string='Consumed in')
