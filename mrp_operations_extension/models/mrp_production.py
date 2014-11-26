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

from openerp import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = super(MrpProduction,
                    self)._action_compute_lines(properties=properties)
        self._get_workorder_in_product_lines(self.workcenter_lines,
                                             self.product_lines)
        return res

    def _get_workorder_in_product_lines(self, workcenter_lines, product_lines):
        for p_line in product_lines:
            for bom_line in self.bom_id.bom_line_ids:
                if bom_line.product_id.id == p_line.product_id.id:
                    for wc_line in workcenter_lines:
                        if wc_line.routing_wc_line.id == bom_line.operation.id:
                            p_line.work_order = wc_line.id
                            break

    def _get_workorder_in_move_lines(self, product_lines, move_lines):
        for move_line in move_lines:
            for product_line in product_lines:
                if product_line.product_id.id == move_line.product_id.id:
                    move_line.work_order = product_line.work_order.id

    @api.multi
    def action_confirm(self):
        produce = False
        if not self.routing_id:
            produce = True
        else:
            for workcenter_line in self.workcenter_lines:
                if workcenter_line.do_production:
                    produce = True
                    break
        if not produce:
            raise exceptions.Warning(
                _('Produce Operation'), _('At least one operation '
                                          'must have checked '
                                          '"Move produced quantity to stock"'
                                          'field'))
        res = super(MrpProduction, self).action_confirm()
        self._get_workorder_in_move_lines(self.product_lines, self.move_lines)
        return res

    @api.multi
    def action_compute(self, properties=None):
        res = super(MrpProduction, self).action_compute(properties=properties)
        self._get_workorder_in_move_lines(self.product_lines, self.move_lines)
        return res


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    work_order = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order')


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    product_line = fields.One2many('mrp.production.product.line',
                                   'work_order', string='Product Lines')
    routing_wc_line = fields.Many2one('mrp.routing.workcenter',
                                      string='Routing WC Line')
    do_production = fields.Boolean(
        string='Move Final Product to Stock')

    @api.model
    def create(self, data):
        workcenter_obj = self.env['mrp.routing.workcenter']
        if 'routing_wc_line' in data:
            routing_wc_line_id = data.get('routing_wc_line')
            work = workcenter_obj.browse(routing_wc_line_id)
            data.update({'do_production':
                         work.operation.do_production})
        return super(MrpProductionWorkcenterLine, self).create(data)
