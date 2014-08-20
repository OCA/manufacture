
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2014 AvanzOSC (Daniel). All Rights Reserved
#    Date: 10/07/2014
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

from openerp import models, fields, tools


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def _bom_explode(self, cr, uid, bom, product, factor, properties=None,
                     level=0, routing_id=False, previous_products=None,
                     master_bom=None, context=None):
        routing_line_obj = self.pool['mrp.routing.workcenter']
        res = super(MrpBom, self)._bom_explode(cr, uid, bom, product, factor,
                                               properties=None, level=0,
                                               routing_id=False,
                                               previous_products=None,
                                               master_bom=None,
                                               context=context)
        result, result2 = res
        for work_order in result2:
            seq = work_order['sequence'] - level
            routing_lines = routing_line_obj.search(cr, uid, [
                ('routing_id', '=', routing_id), ('sequence', '=', seq)])
            routing_line_id = False
            if len(routing_lines) == 1:
                routing_line_id = routing_lines[0]
            elif len(routing_lines) > 1:
                for routing_line in routing_line_obj.browse(cr, uid,
                                                            routing_lines):
                    name_val = tools.ustr(routing_line.name) + ' - '
                    if name_val in work_order['name']:
                        routing_line_id = routing_line.id
                        break
            work_order['routing_wc_line'] = routing_line_id
        return result, result2


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    operation = fields.Many2one('mrp.routing.workcenter', 'Consumed')
