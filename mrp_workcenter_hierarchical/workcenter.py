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

class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'
    _order = 'parent_left'

    def _get_workcenter_ids_to_recompute_level(self, cr, uid, ids, context=None):
        return self.search(cr, uid, [
            '|',
            '|',
            ('parent_id', 'child_of', ids),
            ('id', 'in', ids),
            ('child_ids', 'in', ids),
            ])

    def _get_parent_ids(self, workcenter):
        if workcenter.parent_id:
            ids = self._get_parent_ids(workcenter.parent_id)
            ids.append(workcenter.parent_id.id)
        else:
            ids = []
        return ids

    def _get_parent_level(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        def get_next_level(parent_ids, workcenter):
            return parent_ids and parent_ids.pop(0) or (
                workcenter.child_ids and workcenter.id
                or workcenter.parent_id.id)

        for workcenter in self.browse(cr, uid, ids, context=context):
            parent_ids = self._get_parent_ids(workcenter)
            parent_level_1_id = get_next_level(parent_ids, workcenter)
            parent_level_2_id = get_next_level(parent_ids, workcenter)
            parent_level_3_id = get_next_level(parent_ids, workcenter)
            result[workcenter.id] = {
                'parent_level_1_id': parent_level_1_id,
                'parent_level_2_id': parent_level_2_id,
                'parent_level_3_id': parent_level_3_id,
            }
        return result

    _columns = {
        'parent_id': fields.many2one(
            'mrp.workcenter',
            string='Parent'),
        'child_ids': fields.one2many(
            'mrp.workcenter',
            'parent_id',
            string='Children'),
        'parent_level_1_id': fields.function(
            _get_parent_level,
            relation='mrp.workcenter',
            type='many2one',
            string='Parent Level 1',
            multi='parent_level',
            store={
                'mrp.workcenter': (
                    _get_workcenter_ids_to_recompute_level,
                    ['parent_id'],
                    10),
                },),
        'parent_level_2_id': fields.function(
            _get_parent_level,
            relation='mrp.workcenter',
            type='many2one',
            string='Parent Level 2',
            multi='parent_level',
            store={
                'mrp.workcenter': (
                    _get_workcenter_ids_to_recompute_level,
                    ['parent_id'],
                    10),
                },),
        'parent_level_3_id': fields.function(
            _get_parent_level,
            relation='mrp.workcenter',
            type='many2one',
            string='Parent Level 3',
            multi='parent_level',
            store={
                'mrp.workcenter': (
                    _get_workcenter_ids_to_recompute_level,
                    ['parent_id'],
                    10),
                },),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
    }
