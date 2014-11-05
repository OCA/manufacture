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


class MrpProductionWorkcenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    @api.multi
    def _create_analytic_line(self):
        self.ensure_one()
        analytic_line_obj = self.env['account.analytic.line']
        property_obj = self.env['ir.property']
        task_obj = self.env['project.task']
        if self.workcenter_id.costs_hour > 0.0:
            hour_uom = self.env.ref('product.product_uom_hour', False)
            operation_line = self.operation_time_lines[-1]
            production = self.production_id
            workcenter = self.workcenter_id
            product = workcenter.product_id
            journal_id = workcenter.costs_journal_id or False
            if not journal_id:
                journal_id = self.env.ref(
                    'mrp_production_project_estimated_cost.analytic_journal_'
                    'machines', False)
            analytic_account_id = production.analytic_account_id.id or False
            task_id = False
            if production:
                task = task_obj.search([('mrp_production_id', '=',
                                         production.id),
                                        ('wk_order', '=', False)])
                if task:
                    task_id = task[0].id
            name = ((production.name or '') + '-' +
                    (self.routing_wc_line.operation.code or '') + '-' +
                    (product.default_code or ''))
            general_acc = (
                workcenter.costs_general_account_id.id or
                product.property_account_expense.id or
                product.categ_id.property_account_expense_categ.id or
                property_obj.get('property_account_expense_categ',
                                 'product.category'))
            price = workcenter.costs_hour
            analytic_vals = {'name': name,
                             'ref': name,
                             'date': datetime.now().strftime('%Y-%m-%d'),
                             'user_id': self.env.uid,
                             'product_id': product.id,
                             'product_uom_id': hour_uom.id,
                             'amount': -(price * operation_line.uptime),
                             'unit_amount': operation_line.uptime,
                             'journal_id': journal_id.id,
                             'account_id': analytic_account_id,
                             'general_account_id': general_acc,
                             'task_id': task_id,
                             'mrp_production_id': production.id or False,
                             'workorder': self.id,
                             'estim_avg_cost': 0.0,
                             'estim_std_cost': 0.0
                             }
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
