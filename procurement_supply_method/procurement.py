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

from osv import osv, fields

from tools.translate import _


class ProcurementOrder(osv.osv):
    """
    Procurement Orders
    """
    _inherit = "procurement.order"
    _columns = {
        'supply_method': fields.selection(
            [('produce', _('Produce')), ('buy', _('Buy'))],
            'Supply method',
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)], 'exception': [('readonly', False)]},
            readonly=True),

        # make this field editable when in state draft, confirmed and exception.
        'procure_method': fields.selection(
            [('make_to_stock', _('Make to Stock')), ('make_to_order', _('Make to Order'))],
            _('Procurement Method'),
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)], 'exception': [('readonly', False)]},
            readonly=True, required=True,
            help="If you encode manually a Procurement, you probably want to use"
            " a make to order method."),

    }

    def init(self, cr):
        '''initializes the supply_method field for existing data when this module is first installed.

        NOTE: this method will be executed when this module is installed or upgraded.'''

        cr.execute('update procurement_order set supply_method = pt.supply_method '
                   'from product_product pp, product_template pt '
                   'where procurement_order.supply_method is null '
                   'and procurement_order.product_id = pp.id and pp.product_tmpl_id = pt.id')

    def check_produce(self, cr, uid, ids, context=None):
        """ Checks product supply method.

        Checking the supply_method on the procurement order first.
        @return: True or Product Id.
        """
        for procurement in self.browse(cr, uid, ids, context=context):
            supply_method = procurement.supply_method
            if supply_method:
                if supply_method != 'produce':
                    return False
                elif supply_method == 'service':
                    res = self.check_produce_service(cr, uid, procurement, context)
                else:
                    res = self.check_produce_product(cr, uid, procurement, context)
                if not res:
                    return False
                return True
            else:
                return super(ProcurementOrder, self).check_produce(
                    cr, uid, ids, context=context)

    def check_buy(self, cr, uid, ids, context=None):
        """ Checks supply method.

        Checking the supply_method on the procurement order first.
        @return: True or Product Id.
        """
        for procurement in self.browse(cr, uid, ids, context=context):
            supply_method = procurement.supply_method
            if supply_method:
                if supply_method != 'buy':
                    return False
                else:
                    return True
            else:
                return super(ProcurementOrder, self).check_buy(
                    cr, uid, ids, context=context)


class SaleOrder(osv.osv):
    _inherit = 'sale.order'

    def action_ship_create(self, cr, uid, ids, context=None):
        '''after creating procurement order for the sale order,
        we assign the supply method'''
        if super(SaleOrder, self).action_ship_create(cr, uid, ids, context=context):
            proc_obj = self.pool.get('procurement.order')
            for order in self.browse(cr, uid, ids, context={}):
                for line in order.order_line:
                    if line.procurement_id and line.product_id:
                        proc_obj.write(
                            cr, uid,
                            [line.procurement_id.id],
                            {'supply_method': line.product_id.supply_method})
        return True


class MrpProduction(osv.osv):
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
                procurement_order.write({'supply_method': supply_method}, context=context)
        return super(self._name, self)._hook_create_post_procurement(
            cr, uid, production, procurement_id, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
