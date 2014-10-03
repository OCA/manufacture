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

from openerp import models, fields, tools, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        routing_id = bom.routing_id.id or routing_id
        result, result2 = super(MrpBom, self)._bom_explode(
            bom, product, factor, properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom)
        result2 = self._get_workorder_operations(result2, level=level,
                                                 routing_id=routing_id)
        return result, result2

    def _get_workorder_operations(self, result2, level=0, routing_id=False):
        routing_line_obj = self.env['mrp.routing.workcenter']
        for work_order in result2:
            seq = work_order['sequence'] - level
            routing_lines = routing_line_obj.search([
                ('routing_id', '=', routing_id), ('sequence', '=', seq)])
            routing_line_id = False
            if len(routing_lines) == 1:
                routing_line_id = routing_lines[0].id
            elif len(routing_lines) > 1:
                for routing_line in routing_line_obj.browse(routing_lines):
                    name_val = tools.ustr(routing_line.name) + ' - '
                    if name_val in work_order['name']:
                        routing_line_id = routing_line.id
                        break
            work_order['routing_wc_line'] = routing_line_id
        return result2


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    operation = fields.Many2one('mrp.routing.workcenter', 'Consumed')
