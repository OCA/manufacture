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

from openerp import models, api, fields


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    @api.one
    def _get_prepost_cost(self):
        wc = self.workcenter_id
        self.pre_cost = self.time_start * wc.pre_op_product.cost_price
        self.post_cost = self.time_stop * wc.post_op_product.cost_price

    pre_cost = fields.Float('Pre-Operation Cost', default=_get_prepost_cost)
    post_cost = fields.Float('Post-Operation Cost',
                             default=_get_prepost_cost)

    @api.multi
    def _create_analytic_line(self):
        self.ensure_one()
        analytic_line_obj = self.env['account.analytic.line']
        task_obj = self.env['project.task']
        if self.workcenter_id.costs_hour > 0.0:
            hour_uom = self.env.ref('product.product_uom_hour', False)
            operation_line = self.operation_time_lines[-1]
            production = self.production_id
            workcenter = self.workcenter_id
            product = workcenter.product_id
            journal_id = workcenter.costs_journal_id or self.env.ref(
                'mrp.analytic_journal_machines', False)
            name = ((production.name or '') + '-' +
                    (self.routing_wc_line.operation.code or '') + '-' +
                    (product.default_code or ''))
            general_acc = workcenter.costs_general_account_id or False
            price = -(workcenter.costs_hour * operation_line.uptime)
            analytic_vals = production._prepare_real_cost_analytic_line(
                journal_id, name, production, product,
                general_account=general_acc, workorder=self,
                qty=operation_line.uptime, amount=price)
            task = task_obj.search([('mrp_production_id', '=', production.id),
                                    ('wk_order', '=', False)])
            analytic_vals['task_id'] = task and task[0].id or False
            analytic_vals['product_uom_id'] = hour_uom.id
            analytic_line = analytic_line_obj.create(analytic_vals)
            return analytic_line

    @api.multi
    def _create_pre_post_cost_lines(self, cost_type='pre'):
        self.ensure_one()
        analytic_line_obj = self.env['account.analytic.line']
        task_obj = self.env['project.task']
        hour_uom = self.env.ref('product.product_uom_hour', False)
        production = self.production_id
        workcenter = self.workcenter_id
        journal_id = workcenter.costs_journal_id or self.env.ref(
            'mrp.analytic_journal_machines', False)
        general_acc = workcenter.costs_general_account_id or False
        qty = 0
        price = 0
        product = False
        name = ''
        if cost_type == 'pre':
            product = workcenter.pre_op_product
            name = ((production.name or '') + '-' +
                    (self.routing_wc_line.operation.code or '') + '-PRE-' +
                    (product.default_code or ''))
            price = -(self.pre_cost)
            qty = self.time_start
        elif cost_type == 'post':
            product = workcenter.post_op_product
            name = ((production.name or '') + '-' +
                    (self.routing_wc_line.operation.code or '') + '-POST-' +
                    (product.default_code or ''))
            price = -(self.post_cost)
            qty = self.time_stop
        if price:
            analytic_vals = production._prepare_real_cost_analytic_line(
                journal_id, name, production, product,
                general_account=general_acc, workorder=self,
                qty=qty, amount=price)
            task = task_obj.search([('mrp_production_id', '=', production.id),
                                    ('wk_order', '=', False)])
            analytic_vals['task_id'] = task and task[0].id or False
            analytic_vals['product_uom_id'] = hour_uom.id
            analytic_line_obj.create(analytic_vals)

    @api.multi
    def action_pause(self):
        result = super(MrpProductionWorkcenterLine, self).action_pause()
        self._create_analytic_line()
        return result

    @api.multi
    def action_done(self):
        result = super(MrpProductionWorkcenterLine, self).action_done()
        self._create_analytic_line()
        self._create_pre_post_cost_lines(cost_type='pre')
        self._create_pre_post_cost_lines(cost_type='post')
        return result
