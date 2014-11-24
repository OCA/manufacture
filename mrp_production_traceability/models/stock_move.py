
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


class StockMove(models.Model):
    _inherit = "stock.move"

    prod_parent_lot = fields.Many2one('stock.production.lot',
                                      'Parent production lot')

    @api.multi
    def action_done(self):
        st_move_obj = self.env['stock.move']
        track_lot_obj = self.env['mrp.track.lot']
        res = super(StockMove, self).action_done()
        for final_move in self:
            if final_move.production_id:
                production_id = final_move.production_id.id
                pre_move_ids_assign = st_move_obj.search(
                    [('raw_material_production_id', '=', production_id),
                     ('state', 'not in', ('cancel', 'done'))])
                for move in pre_move_ids_assign:
                    move.prod_parent_lot = final_move.restrict_lot_id.id
                    if (move.restrict_lot_id and
                            move.raw_material_production_id):
                        production = move.raw_material_production_id
                        track_lot_obj.create(
                            {'component': move.product_id.id,
                             'component_lot': move.restrict_lot_id.id,
                             'product': production.product_id.id,
                             'product_lot': final_move.restrict_lot_id.id,
                             'production': production.id,
                             'st_move': move.id})
        return res
