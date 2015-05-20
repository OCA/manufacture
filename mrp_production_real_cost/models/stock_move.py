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


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def create_produce_cost_line(self, amount):
        task_obj = self.env['project.task']
        analytic_line_obj = self.env['account.analytic.line']
        for record in self:
            if amount > 0.0:
                if record.production_id:
                    product = record.product_id
                    production = record.production_id
                    journal_id = self.env.ref(
                        'mrp_production_project_estimated_cost.analytic_'
                        'journal_materials', False)
                    name = ('Final product - ' + (production.name or '') +
                            '-' + (product.default_code or ''))
                    vals = production._prepare_cost_analytic_line(
                        journal_id, name, production, product,
                        qty=record.product_qty, amount=amount)
                    task = task_obj.search(
                        [('mrp_production_id', '=', production.id),
                         ('wk_order', '=', False)])
                    vals['task_id'] = task and task[0].id or False
                    analytic_line_obj.create(vals)

    @api.multi
    def action_consume(self, product_qty, location_id=False,
                       restrict_lot_id=False, restrict_partner_id=False,
                       consumed_for=False):
        task_obj = self.env['project.task']
        analytic_line_obj = self.env['account.analytic.line']
        result = super(StockMove, self).action_consume(
            product_qty, location_id=location_id,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id, consumed_for=consumed_for)
        for record in self:
            price = record.product_id.cost_price
            if price > 0.0:
                if record.raw_material_production_id:
                    product = record.product_id
                    journal_id = self.env.ref(
                        'mrp_production_project_estimated_cost.analytic_'
                        'journal_materials', False)
                    production = record.raw_material_production_id
                    name = (
                        (production.name or '') + '-' +
                        (record.work_order.routing_wc_line.operation.code or
                         '') + '-' + (product.default_code or ''))
                    analytic_vals = production._prepare_cost_analytic_line(
                        journal_id, name, production, product,
                        workorder=record.work_order, qty=record.product_qty,
                        amount=(-price * record.product_qty))
                    task = task_obj.search(
                        [('mrp_production_id', '=', production.id),
                         ('wk_order', '=', False)])
                    analytic_vals['task_id'] = task and task[0].id or False
                    analytic_line_obj.create(analytic_vals)
        return result

    @api.multi
    def product_price_update_production_done(self):
        for move in self:
            if (move.production_id) and (move.product_id.cost_method ==
                                         'average'):
                prod_total_cost = move.production_id.calc_mrp_real_cost()
                product = move.product_id
                product_avail = product.qty_available
                amount_unit = product.cost_price
                template_avail = product.product_tmpl_id.qty_available
                template_price = product.standard_price
                new_cost_price = ((amount_unit * product_avail +
                                  prod_total_cost) /
                                  ((product_avail >= 0.0 and product_avail or
                                    0.0) + move.product_qty))
                new_std_price = ((template_price * template_avail +
                                  prod_total_cost) /
                                 ((template_avail >= 0.0 and template_avail or
                                   0.0) + move.product_qty))
                product.sudo().write({'cost_price': new_cost_price,
                                      'standard_price': new_std_price})

    @api.model
    def get_price_unit(self, move):
        if move.production_id:
            return move.production_id.calc_mrp_real_cost() / move.product_qty
        else:
            return super(StockMove, self).get_price_unit(move)
