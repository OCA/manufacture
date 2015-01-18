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

from openerp import models, fields


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
    op_number = fields.Integer('# operators', default='0')
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type')
