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
            'Load (h)',
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

    def _add_sql_clauses(self, cr, uid, workcenter_ids, context=None):
        states_clause = "'%s'" % "', '".join(ACTIVE_PRODUCTION_STATES)
        workcenters_clause = ", ".join([str(x) for x in workcenter_ids])
        return (states_clause, workcenters_clause)

    def _get_sql_query(self, cr, uid, workcenter_ids, context=None):
        query = """
            SELECT wl.workcenter_id AS workcenter, sum(wl.hour) AS hour
            FROM mrp_production_workcenter_line wl
                LEFT JOIN mrp_production mp ON wl.production_id = mp.id
            WHERE mp.state IN (%s) and wl.workcenter_id IN (%s)
            GROUP BY wl.workcenter_id
        """ % (self._add_sql_clauses(cr, uid, workcenter_ids,
                                     context=context))
        return query

    def _prepare_load_vals(self, cr, uid, result, context=None):
        vals = {}
        for elm in result:
            vals[elm['workcenter']] = {'load': elm['hour']}
        return vals

    def auto_recompute_load(self, cr, uid, domain=None, context=None):
        if not domain:
            domain = []
        ids = self.search(cr, uid, domain, context=context)
        return self.recompute_load(cr, uid, ids, context=context)

    def recompute_load(self, cr, uid, ids, context=None):
        cr.execute(self._get_sql_query(cr, uid, ids, context=context))
        result = cr.dictfetchall()
        if result:
            vals = self._prepare_load_vals(
                cr, uid, result, context=context)
            vals = self._compute_resource_availability(
                cr, uid, ids, vals, context=context)
            for workcenter_id, values in vals.items():
                self.write(cr, uid, workcenter_id, values, context=context)
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

    def _compute_resource_availability(self, cr, uid, ids, vals,
                                       context=None):
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
            capacity = self._get_capacity(cr, uid, workc, context=context)
            calendar = self._get_calendar(cr, uid, workc, context=context)
            date_end = None
            if vals[workc.id].get('load'):
                res = calendar_obj.interval_get(
                    cr, uid, calendar.id, now, vals[workc.id]['load'])
                if res:
                    date_end = res[-1][-1]
            vals[workc.id].update({
                'date_end': date_end,
                'capacity': capacity,
                })
        return vals

    def toogle_online(self, cr, uid, ids, context=None):
        " Called by button in tree view "
        for elm in self.browse(cr, uid, ids, context=context):
            online = True
            online_ids = ids
            if elm.online:
                online = False
            vals = {'online': online}
            self.write(cr, uid, online_ids, vals, context=context)
        if self._to_recompute(cr, uid, context=context):
            context.update({'method_from': 'toogle_online'})
            self._compute_load(cr, uid, context=context)
        action = {
            'view_mode': 'tree,form',
            'context': {'search_default_group_by_workcenter': 1},
        }
        action.update(WORKCENTER_ACTION)
        return action
