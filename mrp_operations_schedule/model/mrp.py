# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, osv, orm
from datetime import datetime


class MrpProduction(orm.Model):

    _inherit = "mrp.production"

    def _compute_planned_workcenter(self, cr, uid, ids, context=None, mini=False):
        return False

    def _reschedule_workorders(self, cr, uid, ids, context=None):
        """ Reschedules the work orders"""
        dt_end = datetime.now()
        if context is None:
            context = {}
        for po in self.browse(cr, uid, ids, context=context):
            dt = dt_end = datetime.strptime(
                po.date_planned, '%Y-%m-%d %H:%M:%S')
            if not po.date_start:
                self.write(cr, uid, [po.id], {
                    'date_start': po.date_planned
                }, context=context, update=False)
            old = None
            for wci in range(len(po.workcenter_lines)):
                wc = po.workcenter_lines[wci]
                if old is None:
                    dt = wc.date_start or dt_end
                if old and wc.sequence > old:
                    dt = dt_end
                if not wc.date_start:
                    self.pool.get('mrp.production.workcenter.line').write(
                        cr, uid, [wc.id],
                        {'date_planned': dt.strftime('%Y-%m-%d %H:%M:%S')},
                        context=context, update=False)
                date_end = wc.date_finished or wc.date_planned_end
                dt_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
                old = wc.sequence or 0
            super(MrpProduction, self).write(cr, uid, [po.id], {
                'date_finished': dt_end
            })
        return dt_end


    def _get_gantt_dates(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for production in self.browse(cr, uid, ids, context=context):
            # Planned production start, actual production start and end
            # are considered in the first place.
            res[production.id] = {}
            if production.date_planned:
                res[production.id]['date_start_gantt'] = \
                    production.date_planned
            if production.date_start:
                res[production.id]['date_start_gantt'] = \
                    production.date_start
            if production.date_finished:
                res[production.id]['date_end_gantt'] = \
                    production.date_finished

            start_dates = []
            end_dates = []
            for workorder in production.workcenter_lines:
                # Add the actual start date if found. Otherwise the planned
                # start date.
                date_start = (workorder.date_start or workorder.date_planned
                              or False)
                if date_start:
                    start_dates.append(date_start)
                date_end = (workorder.date_finished or workorder.date_planned_end
                            or False)
                if date_end:
                    end_dates.append(date_end)
            # Calculate the earliest and latest dates from workorders
            min_start_date = False
            max_end_date = False
            if start_dates:
                min_start_date = min(start_dates)
            if end_dates:
                max_end_date = max(end_dates)
            # Apply workorders earliest and latest dates, ignoring the dates
            #  from the manufacturing orders
            if min_start_date:
                res[production.id]['date_start_gantt'] = min_start_date
            if max_end_date:
                res[production.id]['date_end_gantt'] = max_end_date
        return res

    _columns = {
        'date_start_gantt': fields.function(_get_gantt_dates,
                                            string='Gantt start date',
                                            type='datetime',
                                            multi='gantt_dates'),
        'date_end_gantt': fields.function(_get_gantt_dates,
                                          string='Gantt end date',
                                          type='datetime',
                                          multi='gantt_dates'),
    }

    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """ Computes bills of material of a product and planned date of
        work order.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        result = super(MrpProduction, self).action_compute(
            cr, uid, ids, properties=properties, context=context)
        self._reschedule_workorders(cr, uid, ids, context=context)
        return result


class MrpProductionWorkcenterLine(orm.Model):

    _inherit = "mrp.production.workcenter.line"

    def _get_date_end(self, cr, uid, ids, field_name, arg, context=None):
        """ Finds ending date.
        @return: Dictionary of values.
        """
        ops = self.browse(cr, uid, ids, context=context)
        date_and_hours_by_cal = []
        for op in ops:
            date_start = op.date_start or op.date_planned
            if date_start:
                date_and_hours_by_cal.extend(
                    [(date_start, op.hour, op.workcenter_id.calendar_id.id)])
        intervals = self.pool['resource.calendar'].interval_get_multi(
            cr, uid, date_and_hours_by_cal)

        res = {}
        for op in ops:
            res[op.id] = False
            date_start = op.date_start or op.date_planned
            if date_start:
                i = intervals.get((date_start, op.hour,
                                   op.workcenter_id.calendar_id.id))
                if i:
                    res[op.id] = i[-1][1].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    res[op.id] = date_start
        return res

    def _get_gantt_dates(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for workorder in self.browse(cr, uid, ids, context=context):
            res[workorder.id] = {}
            if workorder.date_planned:
                res[workorder.id]['date_start_gantt'] = \
                    workorder.date_planned
            if workorder.date_start:
                res[workorder.id]['date_start_gantt'] = \
                    workorder.date_start
            if workorder.date_planned_end:
                res[workorder.id]['date_end_gantt'] = \
                    workorder.date_planned_end
            if workorder.date_finished:
                res[workorder.id]['date_end_gantt'] = \
                    workorder.date_finished
        return res

    _columns = {
        'date_start_gantt': fields.function(_get_gantt_dates,
                                            string='Gantt start date',
                                            type='datetime',
                                            multi='gantt_dates'),
        'date_end_gantt': fields.function(_get_gantt_dates,
                                          string='Gantt end date',
                                          type='datetime',
                                          multi='gantt_dates'),
        'date_planned_end': fields.function(_get_date_end,
                                            string='End Date',
                                            type='datetime',
                                            store=False),
    }

    def write(self, cr, uid, ids, vals, context=None, update=True):
        result = super(MrpProductionWorkcenterLine, self).write(
            cr, uid, ids, vals, context=context)
        prod_obj = self.pool.get('mrp.production')
        if vals.get('date_start', False) or vals.get('date_finished', False) \
                or vals.get('date_planned_end', False):
            for prod in self.browse(cr, uid, ids, context=context):
                if prod.production_id.workcenter_lines:
                    prod_obj._reschedule_workorders(cr, uid,
                                                    prod.production_id.id,
                                                    context=context)
        return result
