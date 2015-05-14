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

from openerp import models, api
from datetime import datetime
import math


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def action_consume(self, product_qty, location_id=False,
                       restrict_lot_id=False, restrict_partner_id=False,
                       consumed_for=False):
        task_obj = self.env['project.task']
        property_obj = self.env['ir.property']
        analytic_line_obj = self.env['account.analytic.line']
        result = super(StockMove, self).action_consume(
            product_qty, location_id=location_id,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id, consumed_for=consumed_for)
        for record in self:
            price = record.product_id.standard_price
            if price > 0.0:
                if record.production_id or record.raw_material_production_id:
                    product = record.product_id
                    journal_id = self.env.ref(
                        'mrp_production_project_estimated_cost.analytic_'
                        'journal_materials', False)
                    production_id = False
                    analytic_account_id = False
                    task_id = False
                    if record.production_id:
                        production = record.production_id
                    elif record.raw_material_production_id:
                        production = record.raw_material_production_id
                    if production:
                        production_id = production.id
                        analytic_account_id = production.analytic_account_id.id
                        task = task_obj.search(
                            [('mrp_production_id', '=', production_id),
                             ('wk_order', '=', False)])
                        if task:
                            task_id = task[0].id
                    name = (
                        (production.name or '') + '-' +
                        (record.work_order.routing_wc_line.operation.code or
                         '') + '-' + (product.default_code or ''))
                    general_account = (
                        product.property_account_expense.id or
                        product.categ_id.property_account_expense_categ.id or
                        property_obj.get('property_account_expense_categ',
                                         'product.category'))
                    date = datetime.now().strftime('%Y-%m-%d')
                    uom_id = record.product_id.uom_id.id
                    if record.raw_material_production_id:
                        analytic_vals = {'name': name,
                                         'ref': name,
                                         'date': date,
                                         'user_id': self.env.uid,
                                         'product_id': product.id,
                                         'product_uom_id': uom_id,
                                         'amount': -(price * product_qty),
                                         'unit_amount': product_qty,
                                         'journal_id': journal_id.id,
                                         'account_id': analytic_account_id,
                                         'general_account_id': general_account,
                                         'task_id': task_id,
                                         'mrp_production_id': production_id,
                                         'workorder': record.work_order.id,
                                         'estim_avg_cost': 0.0,
                                         'estim_std_cost': 0.0
                                         }
                        analytic_line_obj.create(analytic_vals)
                    elif record.production_id:
                        amount = 0.0
                        unit_amount = 0.0
                        for wc in production.workcenter_lines:
                            cycle_cost = wc.workcenter_id.costs_cycle
                            cycle_units = wc.workcenter_id.capacity_per_cycle
                            cycle = int(math.ceil(product_qty / cycle_units))
                            amount += cycle * cycle_cost
                            unit_amount += cycle
                        analytic_vals = {'name': name,
                                         'ref': name,
                                         'date': date,
                                         'user_id': self.env.uid,
                                         'product_id': product.id,
                                         'product_uom_id': uom_id,
                                         'amount': amount,
                                         'unit_amount': unit_amount,
                                         'journal_id': journal_id.id,
                                         'account_id': analytic_account_id,
                                         'general_account_id': general_account,
                                         'task_id': task_id,
                                         'mrp_production_id': production_id,
                                         'workorder': record.work_order.id,
                                         'estim_avg_cost': 0.0,
                                         'estim_std_cost': 0.0
                                         }
                        analytic_line_obj.create(analytic_vals)
        return result

    @api.multi
    def product_price_update_before_done(self):
        analytic_line_obj = self.env['account.analytic.line']
        super(StockMove, self).product_price_update_before_done()
        for move in self:
            # adapt standard price on production final moves if the
            # product cost_method is 'average'
            if (move.production_id) and (move.product_id.cost_method ==
                                         'average'):
                analytic_lines = analytic_line_obj.search(
                    [('mrp_production_id', '=', move.production_id.id)])
                prod_total_cost = sum([-line.amount for line in
                                       analytic_lines])
                product = move.product_id
                product_avail = product.qty_available
                amount_unit = product.standard_price
                new_std_price = ((amount_unit * product_avail +
                                  prod_total_cost) /
                                 ((product_avail >= 0.0 and product_avail or
                                   0.0) + move.product_qty))
                # Write the standard price, as SUPERUSER_ID because a warehouse
                # manager may not have the right to write on products
                product.sudo().write({'standard_price': new_std_price})

    @api.multi
    def get_price_unit(self):
        self.ensure_one()
        if self.production_id:
            analytic_line_obj = self.env['account.analytic.line']
            analytic_lines = analytic_line_obj.search(
                [('mrp_production_id', '=', self.production_id.id)])
            return (sum([-line.amount for line in analytic_lines]) /
                    self.product_qty)
        else:
            return super(StockMove, self).get_price_unit()
