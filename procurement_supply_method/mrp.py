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


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    def _hook_create_post_procurement(
            self, cr, uid, production, procurement_id, context=None):
        '''write back the supply_method to the procurement order'''

        if procurement_id:
            procurement_obj = self.pool.get('procurement.order')
            procurement_order = procurement_obj.browse(
                cr, uid, procurement_id, context=context)
            product_id = procurement_order.product_id
            if not procurement_order.supply_method:
                supply_method = product_id.supply_method
                procurement_order.write(
                    {'supply_method': supply_method}, context=context)
        return super(MrpProduction, self)._hook_create_post_procurement(
            cr, uid, production, procurement_id, context=context)
