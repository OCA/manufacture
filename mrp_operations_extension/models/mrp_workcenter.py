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


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    @api.one
    @api.depends('operators')
    def _operators_number_avg_cost(self):
        self.op_number = len(self.operators)
        op_avg_cost = 0.0
        for operator in self.operators:
            op_avg_cost += operator.employee_ids[0].product_id.standard_price
        self.op_avg_cost = op_avg_cost / (self.op_number or 1)

    pre_op_product = fields.Many2one('product.product',
                                     string='Pre Operation Cost')
    post_op_product = fields.Many2one('product.product',
                                      string='Post Operation Cost')
    rt_operations = fields.Many2many(
        'mrp.routing.operation', 'mrp_operation_workcenter_rel', 'workcenter',
        'operation', 'Routing Operations')
    operators = fields.Many2many('res.users', 'mrp_wc_operator_rel',
                                 'workcenter_id', 'operator_id', 'Operators')
    op_number = fields.Integer(
        string='# Operators', compute=_operators_number_avg_cost)
    op_avg_cost = fields.Float(
        string='Operator average cost',
        digits=dp.get_precision('Product Price'))
