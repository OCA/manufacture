# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, context=None):
        '''after creating procurement order for the sale order,
        we assign the supply method'''
        if super(SaleOrder, self).action_ship_create(
                cr, uid, ids, context=context):
            proc_obj = self.pool.get('procurement.order')
            for order in self.browse(cr, uid, ids, context={}):
                for line in order.order_line:
                    if line.procurement_id and line.product_id:
                        proc_obj.write(
                            cr, uid,
                            [line.procurement_id.id],
                            {'supply_method': line.product_id.supply_method})
        return True
