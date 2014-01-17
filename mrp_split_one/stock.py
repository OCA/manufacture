# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
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
"""MRP Split one unit in a production order."""
from openerp.osv import orm
from tools.translate import _


class stock_move(orm.Model):

    """We add to the stock.move methods for the split one button."""

    _inherit = 'stock.move'

    def split_one(self, cr, uid, ids, context=None):
        """Split the current move creating one with quantity one.

        Return action.

        """

        if context is None:
            context = {}

        for move in self.browse(cr, uid, ids, context=context):
            if move.product_qty <= 1.0:
                raise orm.except_orm(
                    _('Error'),
                    _('Quantity needs to be more that 1.')
                )

            self.write(cr, uid, move.id, {
                'product_qty': move.product_qty - 1.0,
                'product_uos_qty': move.product_uos_qty - 1.0,
            }, context=context)
            default_val = {
                'product_qty': 1.0,
                'product_uos_qty': 1.0,
                'state': move.state,
                'prodlot_id': False,
            }
            #create the new move
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

    def split_one_finished(self, cr, uid, ids, context=None):
        """Split one unit from the finished products. Return action."""
        return self.split_one(cr, uid, ids, context=context)

    def split_one_to_finish(self, cr, uid, ids, context=None):
        """Split one unit from the products to finish. Return action."""
        return self.split_one(cr, uid, ids, context=context)
