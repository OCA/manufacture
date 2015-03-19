# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: David BEAL
#    Copyright 2015 Akretion
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

from openerp.osv import orm, fields


class SwitchWorkcenter(orm.TransientModel):
    _name = 'switch.workcenter'

    _columns = {
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
            'Workcenter',
            required=True)
    }

    def switch_workcenter(self, cr, uid, ids, context=None):
        MrpProdWorkcLine_m = self.pool['mrp.production.workcenter.line']
        active_ids = context.get('active_ids', [])
        switch_workc = self.browse(cr, uid, ids, context=context)[0]
        vals = {'workcenter_id': switch_workc.workcenter_id.id}
        MrpProdWorkcLine_m.write(cr, uid, active_ids, vals, context=context)
        return True
