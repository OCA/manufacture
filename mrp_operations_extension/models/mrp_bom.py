# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
import math


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def _prepare_wc_line(self, wc_use, level=0, factor=1):
        res = super(MrpBom, self)._prepare_wc_line(
            wc_use, level=level, factor=factor)
        cycle = int(math.ceil(factor / (wc_use.cycle_nbr or 1)))
        hour = wc_use.hour_nbr * cycle
        default_wc_line = wc_use.op_wc_lines.filtered(lambda r: r.default)
        if default_wc_line.custom_data:
            time_start = default_wc_line.time_start
            time_stop = default_wc_line.time_stop
        else:
            time_start = default_wc_line.workcenter.time_start
            time_stop = default_wc_line.workcenter.time_stop
        res.update({
            'cycle': cycle,
            'hour': hour,
            'time_start': time_start,
            'time_stop': time_stop,
            'routing_wc_line': wc_use.id,
            'do_production': wc_use.do_production,
        })
        return res

    @api.model
    def _prepare_consume_line(self, bom_line, quantity, factor=1):
        res = super(MrpBom, self)._prepare_consume_line(
            bom_line, quantity, factor=factor)
        res['bom_line'] = bom_line.id
        return res

    @api.multi
    @api.onchange('routing_id')
    def onchange_routing_id(self):
        for line in self.bom_line_ids:
            line.operation = self.routing_id.workcenter_lines[:1]
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
