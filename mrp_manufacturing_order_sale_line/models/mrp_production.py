# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    customer = fields.Many2one('res.partner', string='Customer')
    sale_line = fields.Many2one('sale.order.line', string='Sale Line')

    @api.model
    def create(self, data):
        move_obj = self.env['stock.move']
        if 'move_prod_id' in data:
            move_prod_id = data.get('move_prod_id', False)
            if move_prod_id:
                move = move_obj.search([('id', '=', move_prod_id)], limit=1)
                sale_line = move.procurement_id.sale_line_id
                data.update({'sale_line': sale_line.id,
                             'customer': sale_line.order_id.partner_id.id})
        return super(MrpProduction, self).create(data)
