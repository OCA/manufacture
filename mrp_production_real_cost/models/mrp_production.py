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


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.one
    @api.depends('analytic_line_ids', 'analytic_line_ids.amount',
                 'product_qty')
    def get_real_cost(self):
        self.real_cost = sum([-line.amount for line in
                             self.analytic_line_ids])
        self.unit_real_cost = self.real_cost / self.product_qty

    real_cost = fields.Float("Total Real Cost", compute="get_real_cost",
                             store=True)
    unit_real_cost = fields.Float("Unit Real Cost", compute="get_real_cost",
                                  store=True)

    @api.multi
    def action_production_end(self):
        res = super(MrpProduction, self).action_production_end()
        analytic_line_obj = self.env['account.analytic.line']
        for record in self:
            cost_lines = analytic_line_obj.search([('mrp_production_id', '=',
                                                    record.id)])
            record.real_cost = sum([-line.amount for line in cost_lines])
        return res
