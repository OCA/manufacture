# -*- coding: utf-8 -*-
##############################################################################
#
#  license AGPL version 3 or later
#  see license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields


class SwitchScheduleState(orm.TransientModel):
    _name = 'switch.schedule_state'

    def _get_state(self, cr, uid, context=None):
        active_ids = context.get('active_ids', [])
        result = self.pool['mrp.production']._get_values_from_selection(
            cr, uid, active_ids, 'schedule_state', context=context)
        return result

    _columns = {
        'schedule_state': fields.selection(
            _get_state,
            string='Schedule State',
            required=True)
    }

    def switch_schedule_state(self, cr, uid, ids, context=None):
        MrpProduction = self.pool['mrp.production']
        active_ids = context.get('active_ids', [])
        prod_ids = MrpProduction.search(
            cr, uid, [('id', 'in', active_ids)], context=context)
        switch_schedule = self.browse(cr, uid, ids, context=context)[0]
        vals = {'schedule_state': switch_schedule.schedule_state}
        MrpProduction.write(cr, uid, prod_ids, vals, context=context)
        return True
