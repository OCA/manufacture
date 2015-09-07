# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
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
