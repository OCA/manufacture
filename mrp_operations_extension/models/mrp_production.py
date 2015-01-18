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
    def action_confirm(self):
        if (self.routing_id and
                not any([x.do_production for x in self.workcenter_lines])):
            raise exceptions.Warning(
                _("At least one work order must have checked 'Produce here'"))
        return super(MrpProduction, self).action_confirm()

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = super(MrpProduction, self)._action_compute_lines(
            properties=properties)
        self._get_workorder_in_product_lines(
            self.workcenter_lines, self.product_lines, properties=properties)
        return res

    def _get_workorder_in_product_lines(
            self, workcenter_lines, product_lines, properties=None):
        for p_line in product_lines:
            for bom_line in self.bom_id.bom_line_ids:
                if bom_line.product_id.id == p_line.product_id.id:
                    for wc_line in workcenter_lines:
                        if wc_line.routing_wc_line.id == bom_line.operation.id:
                            p_line.work_order = wc_line.id
                            break
                elif bom_line.type == 'phantom':
                    bom_obj = self.env['mrp.bom']
                    bom_id = bom_obj._bom_find(
                        product_id=bom_line.product_id.id,
                        properties=properties)
                    for bom_line2 in bom_obj.browse(bom_id).bom_line_ids:
                        if bom_line2.product_id.id == p_line.product_id.id:
                            for wc_line in workcenter_lines:
                                if (wc_line.routing_wc_line.id ==
                                        bom_line2.operation.id):
                                    p_line.work_order = wc_line.id
                                    break

    @api.model
    def _make_production_consume_line(self, line):
        res = super(MrpProduction, self)._make_production_consume_line(line)
        if line.work_order and res:
            st_move_obj = self.env['stock.move']
            move = st_move_obj.browse(res)
            move.work_order = line.work_order.id
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
    do_production = fields.Boolean(string='Produce here')
