
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 25/08/2014
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

from openerp import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode, wiz=False, context=None):
        st_move_obj = self.pool['stock.move']
        pre_move_ids_assign = st_move_obj.search(
            cr, uid,
            [('raw_material_production_id', '=', production_id),
             ('state', 'not in', ('done', 'cancel'))], context=context)
        pre_move_ids = st_move_obj.search(
            cr, uid, [('raw_material_production_id', '=', production_id)],
            context=context)
        res = super(MrpProduction, self).action_produce(
            cr, uid, production_id, production_qty, production_mode,
            wiz=wiz, context=context)
        if wiz.lot_id:
            post_move_ids = st_move_obj.search(
                cr, uid, [('raw_material_production_id', '=', production_id),
                          ('id', 'not in', pre_move_ids)], context=context)
            if post_move_ids:
                st_move_obj.write(cr, uid, post_move_ids,
                                  {'prod_parent_lot': wiz.lot_id.id})
            else:
                st_move_obj.write(cr, uid, pre_move_ids_assign,
                                  {'prod_parent_lot': wiz.lot_id.id})
        return res
