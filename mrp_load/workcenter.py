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
from openerp.addons.mrp_workcenter_workorder_link.mrp import WORKCENTER_ACTION
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
from collections import defaultdict
import pytz


ACTIVE_PRODUCTION_STATES = ['ready', 'in_production']


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _columns = {
        'online': fields.boolean(
            'Online',
            help="Online workcenters are taken account "
                 "in capacity computing"),
        'load': fields.float(
            'Total Load (h)',
            help="Load for this particular workcenter"),
        'capacity': fields.float(
            'Capacity (h)',
            help="Capacity for this particular workcenter"),
        'date_end': fields.datetime(
            string='Ending Date',
            readonly=True,
            help="Theorical date when all work orders will be done"),
    }

    _defaults = {
        'online': True,
    }

    def _get_sql_load_params(self, cr, uid, ids, context=None):
        return {
            'state': tuple(ACTIVE_PRODUCTION_STATES),
            'workcenter_ids': tuple(ids),
            }

    def _get_sql_load_select(self, cr, uid, ids, context=None):
        return [
            'wl.workcenter_id AS workcenter',
            'sum(wl.hour) AS hour',
            ]

    def _get_sql_load_from(self, cr, uid, ids, context=None):
        return\
        """mrp_production_workcenter_line wl
            LEFT JOIN mrp_production mp ON wl.production_id = mp.id"""

    def _get_sql_load_where(self, cr, uid, ids, context=None):
        return [
            'mp.state IN %(state)s',
            "wl.state != 'done'",
            'wl.workcenter_id IN %(workcenter_ids)s',
            ]

    def _get_sql_load_group(self, cr, uid, ids, context=None):
        return [
            'wl.workcenter_id',
            ]

    def _get_sql_load_query(self, cr, uid, ids, context=None):
        select = self._get_sql_load_select(cr, uid, ids, context=context)
        from_cl = self._get_sql_load_from(cr, uid, ids, context=context)
        where = self._get_sql_load_where(cr, uid, ids, context=context)
        group = self._get_sql_load_group(cr, uid, ids, context=context)
        return\
            "SELECT " + ", ".join(select)\
            + " FROM " + from_cl\
            + " WHERE " + "AND ".join(where)\
            + " GROUP BY " + ", ".join(group)

    def _get_default_workcenter_vals(self, cr, uid, context=None):
        return {
            'load': 0,
            'date_end': None,
            }

    def _set_load_in_vals(self, data, elm):
        data[elm['workcenter']]['load'] += elm['hour']

    def auto_recompute_load(self, cr, uid, domain=None, context=None):
        if not domain:
            domain = []
        ids = self.search(cr, uid, domain, context=context)
        return self.recompute_load(cr, uid, ids, context=context)

    def recompute_load(self, cr, uid, ids, context=None):
        query = self._get_sql_load_query(cr, uid, ids, context=context)
        params = self._get_sql_load_params(cr, uid, ids, context=context)
        cr.execute(query, params)
        result = cr.dictfetchall()
        data = defaultdict(lambda: defaultdict(float))
        for elm in result:
            self._set_load_in_vals(data, elm)
        self._add_capacity_data(cr, uid, ids, data, context=context)
        defaults = self._get_default_workcenter_vals(cr, uid, context=context)
        for workcenter_id in ids:
            vals = defaults.copy()
            vals.update(data[workcenter_id])
            self.write(cr, uid, workcenter_id, vals, context=context)
        return True

    def _get_calendar(self, cr, uid, workcenter, context=None):
        if workcenter.calendar_id:
            return workcenter.calendar_id
        elif workcenter.company_id.calendar_id:
            return workcenter.company_id.calendar_id
        else:
            raise orm.except_orm(
                _('Error !'),
                _('You need to define a calendar for the company !'))

    def _get_capacity_date_to(self, cr, uid, workcenter, date_from,
                              context=None):
        #By default the capacity is computed until the end of the day
        #You can inherit this method to compute it until the end of the week
        #month... or what you want.
        #TODO in a long term make this parametrable
        date_to = datetime(
            date_from.year,
            date_from.month,
            date_from.day) + timedelta(days=1)
        if context and context.get('tz'):
            local_tz = pytz.timezone(context['tz'])
            tz_date_to = local_tz.localize(date_to)
            date_to = tz_date_to.astimezone(pytz.utc).replace(tzinfo=None)
        return date_to

    def _get_capacity(self, cr, uid, workcenter, context=None):
        calendar = self._get_calendar(cr, uid, workcenter, context=context)
        date_from = datetime.now()
        date_to = self._get_capacity_date_to(
            cr, uid, workcenter, date_from, context=context)
        return self.pool['resource.calendar']._interval_hours_get(
            cr, uid, calendar.id, date_from, date_to,
            timezone_from_uid=uid, context=context)

    def _add_capacity_data(self, cr, uid, ids, data, context=None):
        calendar_obj = self.pool['resource.calendar']
        now = datetime.now()
        if context and context.get('tz'):
            # be carefull, resource module will not take in account the time
            # zone. So we have to create a naive localized datetime
            # to send the right information
            local_tz = pytz.timezone(context['tz'])
            tz_now = pytz.utc.localize(now)
            now = tz_now.astimezone(local_tz).replace(tzinfo=None)

        erp_now = now.strftime(DEFAULT_SERVER_DATE_FORMAT)
        for workc in self.browse(cr, uid, ids, context=context):
            date_end = None
            capacity = 0
            if workc.online:
                capacity = self._get_capacity(cr, uid, workc, context=context)
                calendar = self._get_calendar(cr, uid, workc, context=context)
                if data[workc.id].get('load'):
                    res = calendar_obj.interval_get(
                        cr, uid, calendar.id, now, data[workc.id]['load'])
                    if res:
                        date_end = res[-1][-1]
            data[workc.id].update({
                'date_end': date_end,
                'capacity': capacity,
                })

    def set_online(self, cr, uid, ids, context=None):
        return self._set_online_to(cr, uid, ids, True, context=context)

    def set_offline(self, cr, uid, ids, context=None):
        return self._set_online_to(cr, uid, ids, False, context=context)

    def _set_online_to(self, cr, uid, ids, online, context=None):
        self.write(cr, uid, ids, {'online': online}, context=context)
        self.auto_recompute_load(
            cr, uid, domain=[('id', 'in', ids)], context=context)
        return True
