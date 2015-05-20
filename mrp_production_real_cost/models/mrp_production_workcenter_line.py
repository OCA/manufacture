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


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

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
                'mrp_production_project_estimated_cost.analytic_journal_'
                'machines', False)
            name = ((production.name or '') + '-' +
                    (self.routing_wc_line.operation.code or '') + '-' +
                    (product.default_code or ''))
            general_acc = workcenter.costs_general_account_id or False
            price = -(workcenter.costs_hour * operation_line.uptime)
            analytic_vals = production._prepare_cost_analytic_line(
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
    def action_pause(self):
        result = super(MrpProductionWorkcenterLine, self).action_pause()
        self._create_analytic_line()
        return result

    @api.multi
    def action_done(self):
        result = super(MrpProductionWorkcenterLine, self).action_done()
        self._create_analytic_line()
        return result
