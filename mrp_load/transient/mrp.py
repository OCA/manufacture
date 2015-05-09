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
from lxml import etree
from openerp.tools.translate import _


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

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(SwitchWorkcenter, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if context is None:
            context = {}
        if context.get('active_ids') and view_type == 'form':
            line_obj = self.pool['mrp.production.workcenter.line']
            group_id = False
            for line in line_obj.browse(cr, uid, context['active_ids'],
                                        context=context):
                if line.state == 'done':
                    raise orm.except_orm(
                        _('User Error'),
                        _('You can not change the workcenter of a done '
                          'operation'))
                elif not group_id:
                    group_id = line.workcenter_id.workcenter_group_id.id
                elif group_id != line.workcenter_id.workcenter_group_id.id:
                    raise orm.except_orm(
                        _('User Error'),
                        _('You can only swith workcenter of the same group'))
            root = etree.fromstring(res['arch'])
            field = root.find(".//field[@name='workcenter_id']")
            field.set(
                'domain',
                "[('workcenter_group_id', '=', %s)]"\
                % group_id
                )
            orm.setup_modifiers(field, root)
            res['arch'] = etree.tostring(root, pretty_print=True)
        return res
