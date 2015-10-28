# -*- coding: utf-8 -*-
##############################################################################
#
#  license AGPL version 3 or later
#  see license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author Florian da Costa <florian.dacosta@akretion.com>
#
##############################################################################

from openerp.osv import orm


class OrderWorkorder(orm.TransientModel):
    _name = 'order.workorder'

    def order_workorders(self, cr, uid, ids, context=None):
        MrpWorkcenter = self.pool['mrp.workcenter']
        active_ids = context.get('active_ids', [])
        MrpWorkcenter.button_order_workorder(
            cr, uid, active_ids, context=context)
        return True
