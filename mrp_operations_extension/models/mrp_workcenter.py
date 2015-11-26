# -*- coding: utf-8 -*-
# (c) 2015 Avanzosc
# (c) 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    @api.one
    @api.onchange('operators')
    def onchange_operators(self):
        self.op_number = len(self.operators)
        num_oper = 0
        op_avg_cost = 0.0
        for op in self.operators:
            if op.employee_ids[:1].product_id:
                num_oper += 1
                op_avg_cost += op.employee_ids[:1].product_id.standard_price
        self.op_avg_cost = op_avg_cost / (num_oper or 1)

    pre_op_product = fields.Many2one(
        'product.product', string='Pre-operation costing product')
    post_op_product = fields.Many2one(
        'product.product', string='Post-operation costing product')
    rt_operations = fields.Many2many(
        'mrp.routing.operation', 'mrp_operation_workcenter_rel', 'workcenter',
        'operation', 'Routing Operations')
    operators = fields.Many2many(
        'res.users', 'mrp_wc_operator_rel', 'workcenter_id', 'operator_id',
        string='Operators')
    op_number = fields.Integer(string='# Operators')
    op_avg_cost = fields.Float(string='Operator average hourly cost',
                               digits=dp.get_precision('Product Price'))
