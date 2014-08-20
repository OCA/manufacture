
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 28/08/2014
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

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = super(MrpProduction,
                    self)._action_compute_lines(properties=properties)
        workcenter_lines = self.workcenter_lines
        product_lines = self.product_lines
        for p_line in product_lines:
            mrp_bom = self.env['mrp.bom'].search([
                ('routing_id', '=', self.routing_id.id),
                ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)])
            for bom_line in mrp_bom[0].bom_line_ids:
                if bom_line.product_id.id == p_line.product_id.id:
                    for wc_line in workcenter_lines:
                        if wc_line.routing_wc_line.id == bom_line.operation.id:
                            p_line.work_order = wc_line.id
                            break
        return res

    @api.multi
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for move_line in self.move_lines:
            for product_line in self.product_lines:
                if product_line.product_id.id == move_line.product_id.id:
                    move_line.work_order = product_line.work_order.id
        return res


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    work_order = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order')


class mrp_production_workcenter_line(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    product_line = fields.One2many('mrp.production.product.line',
                                   'work_order', string='Product Lines')
    routing_wc_line = fields.Many2one('mrp.routing.workcenter',
                                      string='Routing WC Line')
