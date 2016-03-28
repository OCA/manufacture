# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
            parent_id = False
            for line in line_obj.browse(cr, uid, context['active_ids'],
                                        context=context):
                if line.state == 'done':
                    raise orm.except_orm(
                        _('User Error'),
                        _('You can not change the workcenter of a done '
                          'operation'))
                elif not parent_id:
                    parent_id = line.workcenter_id.parent_level_1_id.id
                elif parent_id != line.workcenter_id.parent_level_1_id.id:
                    raise orm.except_orm(
                        _('User Error'),
                        _('You can only swith workcenter that share the same '
                          'parent level 1'))
            root = etree.fromstring(res['arch'])
            field = root.find(".//field[@name='workcenter_id']")
            field.set(
                'domain',
                "[('parent_level_1_id', '=', %s)]"
                % parent_id
                )
            orm.setup_modifiers(field, root)
            res['arch'] = etree.tostring(root, pretty_print=True)
        return res
