
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

from openerp import models, api, _


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def total_traceability(self):
        """ It traces the information of lots
        @param self: The object pointer.
        @return: A dictionary of values
        """
        track_lot_obj = self.env["mrp.track.lot"]
        for lot in self:
            track_lot_lst = track_lot_obj.search(
                ['|', ('component_lot', '=', lot.id),
                 ('product_lot', '=', lot.id)])
            moves = set()
            for track_lot in track_lot_lst:
                moves |= {move.id for move in track_lot.st_move}
            if moves:
                return {
                    'domain': "[('id','in',[" + ','.join(map(
                        str, list(moves))) + "])]",
                    'name': _('Total Traceability'),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'context': {'tree_view_ref': 'stock.view_move_tree'},
                    'res_model': 'stock.move',
                    'type': 'ir.actions.act_window',
                    }
        return False
