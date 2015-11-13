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
        cycle = (
            wc_use.cycle_nbr and int(math.ceil(factor / wc_use.cycle_nbr)) or
            0)
        hour = wc_use.hour_nbr * cycle
        default_wc_line = wc_use.op_wc_lines.filtered(lambda r: r.default)
        res.update({
            'cycle': cycle,
            'hour': hour,
            'time_start': default_wc_line.time_start or 0.0,
            'time_stop': default_wc_line.time_stop or 0.0,
            'routing_wc_line': wc_use.id,
            'do_production': wc_use.do_production,
        })
        return res

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
