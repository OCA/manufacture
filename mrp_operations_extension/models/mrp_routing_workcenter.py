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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    operation = fields.Many2one('mrp.routing.operation', string='Operation')
    op_wc_lines = fields.One2many('mrp.operation.workcenter',
                                  'routing_workcenter',
                                  'Possible work centers for this operation')
    do_production = fields.Boolean(
        string='Move produced quantity to stock')

    @api.one
    @api.onchange('operation')
    def onchange_operation(self):
        if self.operation:
            self.name = self.operation.name
            self.note = self.operation.description
            op_wc_lst = []
            data = {}
            for operation_wc in self.operation.workcenters:
                data = {
                    'workcenter': operation_wc.id,
                    'capacity_per_cycle': operation_wc.capacity_per_cycle,
                    'time_efficiency': operation_wc.time_efficiency,
                    'time_cycle': operation_wc.time_cycle,
                    'time_start': operation_wc.time_start,
                    'time_stop': operation_wc.time_stop,
                    'default': False,
                    'op_number': self.operation.op_number,
                }
                op_wc_lst.append(data)
            self.op_wc_lines = op_wc_lst

    @api.one
    @api.onchange('workcenter_id')
    def onchange_workcenter(self):
        if self.workcenter_id:
            self.hour_nbr = self.workcenter_id.time_cycle
            for line in self.op_wc_lines:
                line.default = False
                if line.workcenter == self.workcenter_id:
                    line.default = True

    @api.one
    @api.onchange('op_wc_lines')
    def onchange_lines_default(self):
        default = 0
        for line in self.op_wc_lines:
            if line.default:
                self.workcenter_id = line.workcenter
                default += 1
            if default > 1:
                raise exceptions.Warning(_('There is another line set as'
                                           ' default, disable it first.'))
