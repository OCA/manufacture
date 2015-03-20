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


COMPLEX_WORK_ORDER_FIELDS = [
    'message_follower_ids',
    'message_is_follower',
    'message_unread',
    'criterious_output',
]


class MrpWorkcenterOrdering(orm.Model):
    _name = 'mrp.workcenter.ordering'
    _description = "Workcenter Ordering"
    _order = 'sequence'

    _columns = {
        'sequence': fields.integer(
            'Sequence'),
        'workcenter_id': fields.many2one(
            'mrp.workcenter',
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
            string='Type'),
        'order': fields.selection(
            [('asc', 'Asc'), ('desc', 'Desc')],
            string='Order'),
    }

    _defaults = {
        'order': 'asc',
    }


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _columns = {
        'unable_load': fields.float('Unable'),
        'todo_load': fields.float('Todo'),
        'scheduled_load': fields.float('Scheduled'),
        'ordering_field_ids': fields.one2many(
            'mrp.workcenter.ordering',
            'workcenter_id',
            string='Ordering fields',
            help="Allow to define Work Orders ordering priority"),
    }

    def _get_sql_query(self, cr, uid, ids, context=None):
        query = super(MrpWorkcenter, self)._get_sql_query(
            cr, uid, ids, context=context)
        query = (query.replace("FROM", ", mp.schedule_state\nFROM")
                      .replace("GROUP BY wl.workcenter_id",
                               "GROUP BY wl.workcenter_id, mp.schedule_state"))
        return query

    def _prepare_load_vals(self, cr, uid, result, context=None):
        super(MrpWorkcenter, self)._prepare_load_vals(
            cr, uid, result, context=context)
        vals = {}
        for elm in result:
            sched = elm['schedule_state']
            workcenter = elm['workcenter']
            if workcenter not in vals:
                vals[workcenter] = {
                    'load': elm['hour'],
                    '%s_load' % sched: elm['hour'],
                }
            else:
                vals[workcenter]['load'] += elm['hour']
                if '%s_load' % sched in vals[workcenter]:
                    vals[workcenter]['%s_load' % sched] += elm['hour']
                else:
                    vals[workcenter]['%s_load' % sched] = elm['hour']
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
