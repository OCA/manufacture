
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Date: 04/11/2014
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
from openerp import models, fields


class MrpTrackLot(models.Model):
    _name = "mrp.track.lot"

    component = fields.Many2one('product.product', 'Component')
    component_lot = fields.Many2one('stock.production.lot', 'Component Lot')
    product = fields.Many2one('product.product', 'Final Product')
    product_lot = fields.Many2one('stock.production.lot', 'Final Product Lot')
    production = fields.Many2one('mrp.production', 'Production')
    st_move = fields.Many2one('stock.move', 'Stock Move')
