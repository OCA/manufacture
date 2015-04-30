# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp import SUPERUSER_ID


class MrpProduction(orm.Model):

    _inherit = 'mrp.production'

    def _action_compute_lines(self, cr, uid, ids, properties=None, context=None):
        super(MrpProduction, self)._action_compute_lines(
            cr, uid, ids, properties=properties, context=context)
        prod_line_obj = self.pool.get('mrp.production.product.line')
        results = []
        for production in self.browse(cr, uid, ids, context=context):
            product_qty = {}
            product_uos_qty = {}
            line_vals = {}
            for line in production.product_lines:
                key = '%s:%s:%s' \
                      % (line.product_id, line.product_uom, line.product_uos, )
                if key in line_vals.keys():
                    product_qty[key] += line.product_qty
                    product_uos_qty[key] += line.product_uos_qty
                else:
                    line_vals[key] = {
                        'name': line.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'product_uos': line.product_uos and
                        line.product_uos.id or False
                    }
                    product_qty[key] = line.product_qty
                    product_uos_qty[key] = line.product_uos_qty
            for key in line_vals.keys():
                results.append({
                    'name': line_vals[key]['name'],
                    'product_id': line_vals[key]['product_id'],
                    'product_qty': product_qty[key],
                    'product_uom': line_vals[key]['product_uom'],
                    'product_uos_qty': product_uos_qty[key],
                    'product_uos': line_vals[key]['product_uos'],
                })

            # unlink product_lines
            prod_line_obj.unlink(cr, SUPERUSER_ID,
                                 [line.id for line in production.product_lines],
                                 context=context)
            # reset product_lines in production order
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
        return results
