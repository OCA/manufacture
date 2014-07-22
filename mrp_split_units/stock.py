# -*- coding: utf-8 -*-
"""Add to the stock move the methods to split MO lines."""
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2014 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from osv import orm
from tools.translate import _
import decimal_precision as dp


class stock_move(orm.Model):

    """Stock move. Add methods to split moves in manufacturing orders."""

    _inherit = 'stock.move'

    def split_units(self, cr, uid, ids, context=None):
        """Split the current move creating moves with quantity one.

        Return an action to reload the current record as a poor man's refresh.

        """

        def almost_integer(cr, qty, int_qty):
            return (
                qty - int_qty < 10 ** -dp.get_precision('Product UoM')(cr)[1]
            )

        for move in self.browse(cr, uid, ids, context=context):
            int_qty = int(move.product_qty)

            if not almost_integer(cr, move.product_qty, int_qty):
                raise orm.except_osv(
                    _('Error'),
                    _('Quantity needs to be integer.')
                )

            if int_qty <= 1:
                raise orm.except_osv(
                    _('Error'),
                    _('Quantity needs to be more than 1.')
                )

            self.write(cr, uid, move.id, {
                'product_qty': 1.0,
                'product_uos_qty': 1.0,
            }, context=context)

            default_val = {
                'product_qty': 1.0,
                'product_uos_qty': 1.0,
                'state': move.state,
                'prodlot_id': False,
            }

            # create the new moves
            for i in xrange(int_qty - 1):
                self.copy(cr, uid, move.id, default_val, context=context)

        # poor man's refresh
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
            'res_id': move.production_id.id,
        }

    def split_units_finished(self, cr, uid, ids, context=None):
        """Split a line in the Finished Products. Return an action."""
        return self.split_units(cr, uid, ids, context=context)

    def split_units_to_finish(self, cr, uid, ids, context=None):
        """Split a line in the Products to Finish. Return an action."""
        return self.split_units(cr, uid, ids, context=context)
