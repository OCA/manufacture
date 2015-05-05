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
from collections import defaultdict

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
    _order = 'date_planned, sequence'

    _columns = {
        'priority': fields.integer('Priority'),
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

    def _get_sql_query(self, cr, uid, ids, context=None):
        query = super(MrpWorkcenter, self)._get_sql_query(
            cr, uid, ids, context=context)
        query = (query.replace("FROM", ", mp.schedule_state\nFROM")
                      .replace("GROUP BY wl.workcenter_id",
                               "GROUP BY wl.workcenter_id, mp.schedule_state"))
        return query

    def _set_load_in_vals(self, vals, elm):
        vals[elm['workcenter']]['%s_load' % elm['schedule_state']] \
            += elm['hour']
        vals[elm['workcenter']]['load'] += elm['hour']

    def _prepare_load_vals(self, cr, uid, result, context=None):
        super(MrpWorkcenter, self)._prepare_load_vals(
            cr, uid, result, context=context)
        vals = defaultdict(lambda: defaultdict(float))
        for elm in result:
            self._set_load_in_vals(vals, elm)
        return vals

    def _erase_cached_data(self, cr, uid, workcenter_ids, context=None):
        " Update to 0 '*load' columns "
        MrpWorkCter_m = self.pool['mrp.workcenter']
        vals = {}
        for col in MrpWorkCter_m._columns:
            if len(col) > 3 and col[-4:] == 'load':
                vals.update({col: 0})
        MrpWorkCter_m.write(cr, uid, workcenter_ids, vals, context=context)
        return True

    def button_order_workorders_in_workcenter(
            self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            ProdLine_m = self.pool['mrp.production.workcenter.line']
            order_by = ['%s %s' % (row.field_id.name, row.order)
                        for row in elm.ordering_field_ids]
            prod_line_ids = ProdLine_m.search(cr, uid, [
                ('state', 'not in', STATIC_STATES),
                ('workcenter_id', '=', elm.id), ],
                order=', '.join(order_by), context=context)
            count = 1
            for prod_line_id in prod_line_ids:
                vals = {'sequence': count}
                count += 1
                ProdLine_m.write(cr, uid, prod_line_id, vals, context=context)
        return True
