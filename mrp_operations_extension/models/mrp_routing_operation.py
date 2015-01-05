# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class MrpOperationWorkcenter(models.Model):
    _name = 'mrp.operation.workcenter'
    _description = 'MRP Operation Workcenter'

    workcenter = fields.Many2one('mrp.workcenter', string='Work Center')
    routing_workcenter = fields.Many2one('mrp.routing.workcenter',
                                         'Routing Workcenter')
    time_efficiency = fields.Float('Efficiency Factor')
    capacity_per_cycle = fields.Float('Capacity per Cycle')
    time_cycle = fields.Float('Time for 1 cycle (hour)',
                              help="Time in hours for doing one cycle.")
    time_start = fields.Float('Time before prod.',
                              help="Time in hours for the setup.")
    time_stop = fields.Float('Time after prod.',
                             help="Time in hours for the cleaning.")
    op_number = fields.Integer('# Operators', default='0')
    op_avg_cost = fields.Float(
        string='Operator Average Cost',
        digits=dp.get_precision('Product Price'))
    default = fields.Boolean('Default')

    @api.one
    @api.onchange('workcenter')
    def onchange_workcenter(self):
        if self.workcenter:
            self.capacity_per_cycle = self.workcenter.capacity_per_cycle
            self.time_efficiency = self.workcenter.time_efficiency
            self.time_cycle = self.workcenter.time_cycle
            self.time_start = self.workcenter.time_start
            self.time_stop = self.workcenter.time_stop
            self.op_number = self.workcenter.op_number
            self.op_avg_cost = self.workcenter.op_avg_cost
            self.default = False

    @api.model
    def create(self, vals):
        res = super(MrpOperationWorkcenter, self).create(vals)
        if vals.get('default', False):
            routing_obj = self.env['mrp.routing.workcenter']
            routing = routing_obj.browse(vals.get('routing_workcenter', False))
            routing.workcenter_id = vals.get('workcenter', False)
            for line in routing.op_wc_lines:
                if line != res:
                    line.default = False
        return res

    @api.multi
    def write(self, vals):
        res = super(MrpOperationWorkcenter, self).write(vals)
        for record in self:
            if vals.get('default', False):
                record.routing_workcenter.workcenter_id = record.workcenter
                for line in record.routing_workcenter.op_wc_lines:
                    if line != record:
                        line.default = False
        return res


class MrpRoutingOperation(models.Model):
    _name = 'mrp.routing.operation'
    _description = 'MRP Routing Operation'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    description = fields.Text('Description')
    steps = fields.Text('Relevant Steps')
    workcenters = fields.Many2many(
        'mrp.workcenter', 'mrp_operation_workcenter_rel', 'operation',
        'workcenter', 'Work centers')
    op_number = fields.Integer('# Operators', default='0')
    do_production = fields.Boolean(
        string='Move Final Product to Stock')
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type')
