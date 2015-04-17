# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields, expression


class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    def get_child_boms(self, cr, uid, ids, context=None):
        result = {}
        for curr_id in ids:
            result[curr_id] = True
        # Now add the children
        cr.execute('''
        WITH RECURSIVE children AS (
        SELECT bom_id, id
        FROM mrp_bom
        WHERE bom_id IN %s
        UNION ALL
        SELECT a.bom_id, a.id
        FROM mrp_bom a
        JOIN children b ON(a.bom_id = b.id)
        )
        SELECT * FROM children order by bom_id
        ''', (tuple(ids),))
        res = cr.fetchall()
        for x, y in res:
            result[y] = True
        return result

    def _is_bom(self, cr, uid, ids, name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        for bom in self.browse(cr, uid, ids, context=context):
            result[bom.id] = False
            if bom.bom_lines:
                result[bom.id] = True
        return result

    def _bom_hierarchy_indent_calc(self, cr, uid, ids, prop, unknow_none,
                                   unknow_dict):
        if not ids:
            return []
        res = []
        for bom in self.browse(cr, uid, ids, context=None):
            data = []
            b = bom
            while b:
                if b.name and b.bom_id:
                    data.insert(0, '>')
                else:
                    data.insert(0, '')

                b = b.bom_id
            data = ''.join(data)
            res.append((bom.id, data))
        return dict(res)

    def _complete_bom_hierarchy_code_calc(
            self, cr, uid, ids, prop, unknow_none, unknow_dict):
        if not ids:
            return []
        res = []
        for bom in self.browse(cr, uid, ids, context=None):
            data = []
            b = bom
            while b:
                if b.code:
                    data.insert(0, b.code)
                else:
                    data.insert(0, '')

                b = b.bom_id
            data = ' / '.join(data)
            data = '[' + data + '] '

            res.append((bom.id, data))
        return dict(res)

    def _complete_bom_hierarchy_name_calc(
            self, cr, uid, ids, prop, unknow_none, unknow_dict):
        if not ids:
            return []
        res = []
        for bom in self.browse(cr, uid, ids, context=None):
            data = []
            b = bom
            while b:
                if b.name:
                    data.insert(0, b.name)
                else:
                    data.insert(0, '')

                b = b.bom_id

            data = ' / '.join(data)
            res.append((bom.id, data))
        return dict(res)

    def _is_parent(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for bom in self.browse(cr, uid, ids, context=None):
            if not bom.bom_id:
                res[bom.id] = True
            else:
                res[bom.id] = False
        return res

    _columns = {
        'is_parent': fields.function(_is_parent, string="Is parent BOM",
                                     type='boolean', readonly=True,
                                     store=True),
        'has_child': fields.function(_is_bom, string="Has components",
                                     type='boolean', readonly=True),
        'bom_hierarchy_indent': fields.function(_bom_hierarchy_indent_calc,
                                                method=True,
                                                type='char', string='Level',
                                                size=32, readonly=True),
        'complete_bom_hierarchy_code': fields.function(
            _complete_bom_hierarchy_code_calc, method=True, type='char',
            string='Full BOM Hierarchy Code', size=250,
            help='The full BOM code describes the full path of this component '
                 'within the BOM hierarchy',
            store={'mrp.bom': (get_child_boms, ['name', 'code',
                                                'bom_id'], 20)}),
        'complete_bom_hierarchy_name': fields.function(
            _complete_bom_hierarchy_name_calc, method=True, type='char',
            string='Full BOM Hierarchy Name', size=250,
            help='Full path in the BOM hierarchy',
            store={'mrp.bom': (get_child_boms, ['name', 'code',
                                                'bom_id'], 20)}),
    }

    _order = 'complete_bom_hierarchy_code'

    def onchange_product_id(self, cr, uid, ids, product_id, name,
                            context=None):
        res = super(mrp_bom, self).onchange_product_id(cr, uid, ids,
                                                       product_id, name,
                                                       context=context)
        if product_id:
            prod = self.pool.get('product.product').browse(
                cr, uid, product_id, context=context)
            if 'value' in res:
                res['value'].update({'code': prod.code})
            else:
                res = {'value': {'name': prod.name,
                                 'code': prod.code,
                                 'product_uom': prod.uom_id.id}}
        return res

    def action_openChildTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        bom = self.browse(cr, uid, ids[0], context)
        child_bom_ids = self.pool.get('mrp.bom').search(
            cr, uid, [('bom_id', '=', bom.id)])
        res = self.pool.get('ir.actions.act_window').for_xml_id(
            cr, uid, 'mrp_bom_hierarchy', 'action_mrp_bom_hierarchy_tree2',
            context)
        res['context'] = {
            'default_bom_id': bom.id,
        }
        res['domain'] = "[('id', 'in', ["+','.join(
            map(str, child_bom_ids))+"])]"
        res['nodestroy'] = False
        return res

    def action_openParentTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        bom = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(
            cr, uid, 'mrp_bom_hierarchy', 'action_mrp_bom_hierarchy_tree2',
            context)
        if bom.bom_id:
            for parent_bom_id in self.pool.get('mrp.bom').search(
                    cr, uid, [('id', '=',
                               bom.bom_id.id)]):
                res['domain'] = "[('id','=',"+str(parent_bom_id)+")]"
        res['nodestroy'] = False
        return res
