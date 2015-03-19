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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as ISO_FORMAT
from datetime import datetime


ACTIVE_PRODUCTION_STATES = ['ready', 'confirmed', 'in_production']


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
        'availability': fields.datetime(
            string='Available',
            readonly=True,
            help="Better availability date if all work orders of "
                 "this workcenter are ready to produce as required"),
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

    def _erase_cached_data(self, cr, uid, workcenter_ids, context=None):
        " Update to 0 'load' column"
        MrpWorkCter_m = self.pool['mrp.workcenter']
        vals = {'load': 0}
        MrpWorkCter_m.write(cr, uid, workcenter_ids, vals, context=context)
        return True

    def _get_workc_domain(self, cr, uid, context=None):
        return [('online', '=', True)]

    def _compute_load(self, cr, uid, context=None):
        domain = self._get_workc_domain(cr, uid, context=context)
        workcenter_ids = self.search(cr, uid, domain, context=context)
        if workcenter_ids:
            self._erase_cached_data(cr, uid, workcenter_ids, context=context)
            # Compute time for workcenters in mrp_production_workcenter_line
            cr.execute(self._get_sql_query(
                cr, uid, workcenter_ids, context=context))
            result = cr.dictfetchall()
            print 'result', result
            if result:
                vals = self._prepare_load_vals(
                    cr, uid, result, context=context)
                print 'vals', vals
                vals = self._compute_resource_availability(
                    cr, uid, workcenter_ids, vals, context=context)
                for workcenter, values in vals.items():
                    self.write(cr, uid, workcenter, values, context=context)
        return True

    def _compute_resource_availability(self, cr, uid, ids, vals,
                                       context=None):
        ResCal_m = self.pool['resource.calendar']
        now = datetime.now()
        erp_now = now.strftime(ISO_FORMAT)
        # horizon = 1  # day
        # vals[workc.id]['load']
        for workc in self.browse(cr, uid, ids, context=context):
            calendar = False
            # user company calendar is used, if not calendar
            if workc.calendar_id:
                calendar = workc.calendar_id.id
            if workc.id in vals:
                # _get_date exclude not working days
                vals[workc.id]['availability'] = ResCal_m._get_date(
                    cr, uid, calendar, now,
                    1, resource=workc.id,
                    context=context).strftime(ISO_FORMAT)
                print vals
            else:
                vals[workc.id] = {'availability': erp_now}
        return vals

    def _to_recompute(self, cr, uid, context=None):
        """ Override in case of performance issue
        """
        return True

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

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if self._to_recompute(cr, uid, context=context):
            context.update({'method_from': 'fields_view_get'})
            self._compute_load(cr, uid, context=context)
        return super(MrpWorkcenter, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
