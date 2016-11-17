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


class ProcurementOrder(osv.osv):
    """
    Procurement Orders
    """
    _inherit = "procurement.order"
    _columns = {
        'supply_method': fields.selection(
            [('produce', 'Produce'), ('buy', 'Buy')],
            'Supply method',
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)],
                    'exception': [('readonly', False)]},
            readonly=True),

        # make this field editable when in state draft,confirmed and exception.
        'procure_method': fields.selection(
            [('make_to_stock', 'Make to Stock'),
             ('make_to_order', 'Make to Order')],
            'Procurement Method',
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)],
                    'exception': [('readonly', False)]},
            readonly=True, required=True,
            help="If you encode manually a Procurement,"
            " you probably want to use a make to order method."),

    }

    def init(self, cr):
        '''initializes the supply_method field for existing data
        when this module is first installed.

        NOTE: this method will be executed
            when this module is installed or upgraded.'''

        cr.execute('update procurement_order '
                   'set supply_method = pt.supply_method '
                   'from product_product pp, product_template pt '
                   'where procurement_order.supply_method is null '
                   'and procurement_order.product_id = pp.id '
                   'and pp.product_tmpl_id = pt.id')

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
                    res = self.check_produce_service(
                        cr, uid, procurement, context)
                else:
                    res = self.check_produce_product(
                        cr, uid, procurement, context)
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
