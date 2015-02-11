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

from openerp import models, api


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.multi
    def do_produce(self):
        track_lot_obj = self.env['mrp.track.lot']
        result = super(MrpProductProduce, self).do_produce()
        production = self.env['mrp.production'].browse(
            self.env.context['active_id'])
        for data in self:
            if data.lot_id:
                for move in production.move_lines2:
                    if not move.prod_parent_lot:
                        move.prod_parent_lot = data.lot_id.id
                        track_lot_obj.create(
                            {'component': move.product_id.id,
                             'component_lot': move.restrict_lot_id.id,
                             'product': production.product_id.id,
                             'product_lot': data.lot_id.id,
                             'production': production.id,
                             'st_move': move.id})
        return result
