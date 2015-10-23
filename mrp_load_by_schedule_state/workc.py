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
from openerp.addons.mrp_workcenter_workorder_link.mrp import STATIC_STATES
from openerp.tools.translate import _


COMPLEX_WORK_ORDER_FIELDS = [
    'message_follower_ids',
    'message_is_follower',
    'message_unread',
]


class MrpWorkcenterOrderingKey(orm.Model):
    _name = 'mrp.workcenter.ordering.key'
    _description = "Workcenter Ordering Key"

    _columns = {
        'name': fields.char('Name'),
        'field_ids': fields.one2many(
            'mrp.workcenter.ordering.field',
            'ordering_key_id',
            'Fields')
    }


class MrpWorkcenterOrderingField(orm.Model):
    _name = 'mrp.workcenter.ordering.field'
    _description = "Workcenter Ordering Field"
    _order = 'sequence ASC'

    _columns = {
        'sequence': fields.integer(
            'Sequence'),
        'ordering_key_id': fields.many2one(
            'mrp.workcenter.ordering.key',
            'Workcenter'),
        'field_id': fields.many2one(
            'ir.model.fields',
            string='Work Order Field',
            domain=[('model', '=', 'mrp.production.workcenter.line'),
                    ('name', 'not in', COMPLEX_WORK_ORDER_FIELDS)],
            help="",),
        'ttype': fields.related(
            'field_id', 'ttype',
            type='char',
            string='Type',
            readonly=True),
        'order': fields.selection(
            [('asc', 'Asc'), ('desc', 'Desc')],
            string='Order'),
    }

    _defaults = {
        'order': 'asc',
    }


class MrpRoutingWorkcenter(orm.Model):
    _inherit = 'mrp.routing.workcenter'

    _columns = {
        'priority': fields.integer('Priority'),
    }


class MrpBom(orm.Model):
    _inherit = 'mrp.bom'

    def _prepare_production_line(self, wc_use, bom, factor, level):
        res = super(MrpBom, self)._prepare_production_line(
            wc_use, bom, factor, level)
        res['priority'] = wc_use.priority
        return res


class MrpProductionWorkcenterLine(orm.Model):
    _inherit = 'mrp.production.workcenter.line'
    _order = 'sequence'

    def _get_operation_from_routing(self, cr, uid, ids, context=None):
        return self.pool['mrp.production.workcenter.line'].search(cr, uid, [
            ['routing_line_id', '=', ids],
            ], context=context)

    _columns = {
        'priority': fields.related(
            'routing_line_id',
            'priority',
            type='integer',
            string='Priority',
            store={
                'mrp.routing.workcenter': [
                    _get_operation_from_routing,
                    ['priority'],
                    10,
                ],
            },
        ),
    }


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _columns = {
        'workcenter_line_ids': fields.one2many(
            'mrp.routing.workcenter',
            'workcenter_id',
            'Work Centers'),
        'waiting_load': fields.float('Waiting (h)'),
        'todo_load': fields.float('Todo (h)'),
        'scheduled_load': fields.float('Scheduled (h)'),
        'ordering_key_id': fields.many2one(
            'mrp.workcenter.ordering.key',
            string='Ordering Key',
            help="Allow to define Work Orders ordering priority"),
    }

    def _get_sql_load_select(self, cr, uid, ids, context=None):
        select = super(MrpWorkcenter, self)._get_sql_load_select(
            cr, uid, ids, context=context)
        select.append('mp.schedule_state')
        return select

    def _get_sql_load_group(self, cr, uid, ids, context=None):
        group = super(MrpWorkcenter, self)._get_sql_load_group(
            cr, uid, ids, context=context)
        group.append('mp.schedule_state')
        return group

    def _set_load_in_vals(self, data, elm):
        super(MrpWorkcenter, self)._set_load_in_vals(data, elm)
        field = '%s_load' % elm['schedule_state']
        data[elm['workcenter']][field] += elm['hour']

    def _get_default_workcenter_vals(self, cr, uid, context=None):
        default = super(MrpWorkcenter, self)._get_default_workcenter_vals(
            cr, uid, context=context)
        for col in self._columns:
            if len(col) > 3 and col[-4:] == 'load':
                default.update({col: 0})
        return default

    def button_order_workorder(self, cr, uid, ids, context=None):
        workorder_obj = self.pool['mrp.production.workcenter.line']
        for workcenter in self.browse(cr, uid, ids, context=context):
            if not workcenter.ordering_key_id:
                raise orm.except_orm(
                    _('User Error'),
                    _('The automatic ordering can not be processed as the '
                      'ordering key is empty. Please go in the tab "Ordering" '
                      'and fill the field "ordering key"'))
            order_by = ['%s %s' % (row.field_id.name, row.order)
                        for row in workcenter.ordering_key_id.field_ids]
            prod_line_ids = workorder_obj.search(cr, uid, [
                ('state', 'not in', STATIC_STATES),
                ('workcenter_id', '=', workcenter.id),
                ], order=', '.join(order_by), context=context)
            count = 1
            for prod_line_id in prod_line_ids:
                vals = {'sequence': count}
                count += 1
                workorder_obj.write(
                    cr, uid, prod_line_id, vals, context=context)
        return True
