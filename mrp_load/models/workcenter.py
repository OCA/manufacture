# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from datetime import datetime, timedelta
from collections import defaultdict
from openerp.tools.translate import _
from openerp.exceptions import UserError
import pytz


ACTIVE_PRODUCTION_STATES = ['ready', 'in_production']


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    online = fields.Boolean(
        string='Online',
        help="Online workcenters are taken account "
             "in capacity computing",
        default=True)
    load = fields.Float(
        string='Total Load (h)',
        help="Load for this particular workcenter")
    capacity = fields.Float(
        string='Capacity (h)',
        help="Capacity for this particular workcenter")
    date_end = fields.Datetime(
        string='Ending Date',
        readonly=True,
        help="Theorical date when all work orders will be done")

    @api.multi
    def _get_sql_load_params(self):
        return {
            'state': tuple(ACTIVE_PRODUCTION_STATES),
            'workcenter_ids': tuple(self.ids),
            }

    @api.multi
    def _get_sql_load_select(self):
        return [
            'wl.workcenter_id AS workcenter',
            'sum(wl.hour) AS hour',
            ]

    @api.multi
    def _get_sql_load_from(self):
        return """mrp_production_workcenter_line wl
            LEFT JOIN mrp_production mp ON wl.production_id = mp.id"""

    @api.multi
    def _get_sql_load_where(self):
        return [
            'mp.state IN %(state)s',
            "wl.state != 'done'",
            'wl.workcenter_id IN %(workcenter_ids)s',
            ]

    @api.multi
    def _get_sql_load_group(self):
        return [
            'wl.workcenter_id',
            ]

    @api.multi
    def _get_sql_load_query(self):
        select = self._get_sql_load_select()
        from_cl = self._get_sql_load_from()
        where = self._get_sql_load_where()
        group = self._get_sql_load_group()
        return\
            "SELECT " + ", ".join(select)\
            + " FROM " + from_cl\
            + " WHERE " + "AND ".join(where)\
            + " GROUP BY " + ", ".join(group)

    @api.model
    def _get_default_workcenter_vals(self):
        return {
            'load': 0,
            'date_end': None,
            }

    @api.multi
    def _set_load_in_vals(self, data, elm):
        data[elm['workcenter']]['load'] += elm['hour']

    @api.model
    def auto_recompute_load(self, domain=None):
        if not domain:
            domain = []
        records = self.search(domain)
        return records.recompute_load()

    @api.multi
    def recompute_load(self):
        query = self._get_sql_load_query()
        params = self._get_sql_load_params()
        self._cr.execute(query, params)
        result = self._cr.dictfetchall()
        data = defaultdict(lambda: defaultdict(float))
        for elm in result:
            self._set_load_in_vals(data, elm)
        self._add_capacity_data(data)
        defaults = self._get_default_workcenter_vals()
        for workcenter in self:
            vals = defaults.copy()
            vals.update(data[workcenter.id])
            workcenter.write(vals)
        return True

    @api.multi
    def _get_calendar(self):
        self.ensure_one()
        if self.calendar_id:
            return self.calendar_id
        elif self.company_id.calendar_id:
            return self.company_id.calendar_id
        else:
            raise UserError(
                _('You need to define a calendar for the company !'))

    @api.multi
    def _get_capacity_date_to(self, date_from):
        # By default the capacity is computed until the end of the day
        # You can inherit this method to compute it until the end of the week
        # month... or what you want.
        # TODO in a long term make this parametrable
        self.ensure_one()
        date_to = datetime(
            date_from.year,
            date_from.month,
            date_from.day) + timedelta(days=1)
        if self._context.get('tz'):
            local_tz = pytz.timezone(self._context['tz'])
            tz_date_to = local_tz.localize(date_to)
            date_to = tz_date_to.astimezone(pytz.utc).replace(tzinfo=None)
        return date_to

    @api.multi
    def _get_capacity(self):
        self.ensure_one()
        calendar = self._get_calendar()
        date_from = datetime.now()
        date_to = self._get_capacity_date_to(date_from)
        return self.env['resource.calendar']._interval_hours_get(
            calendar.id, date_from, date_to,
            timezone_from_uid=self._uid)

    @api.multi
    def _add_capacity_data(self, data):
        calendar_obj = self.env['resource.calendar']
        now = datetime.now()
        if self._context.get('tz'):
            # be carefull, resource module will not take in account the time
            # zone. So we have to create a naive localized datetime
            # to send the right information
            local_tz = pytz.timezone(self._context['tz'])
            tz_now = pytz.utc.localize(now)
            now = tz_now.astimezone(local_tz).replace(tzinfo=None)

        for workcenter in self:
            date_end = None
            capacity = 0
            if workcenter.online:
                capacity = workcenter._get_capacity()
                calendar = workcenter._get_calendar()
                if data[workcenter.id].get('load'):
                    res = calendar_obj.interval_get(
                        calendar.id, now, data[workcenter.id]['load'])
                    if res:
                        date_end = res[-1][-1]
            data[workcenter.id].update({
                'date_end': date_end,
                'capacity': capacity,
                })

    @api.multi
    def set_online(self):
        return self._set_online_to(True)

    @api.multi
    def set_offline(self):
        return self._set_online_to(False)

    @api.multi
    def _set_online_to(self, online):
        self.write({'online': online})
        self.auto_recompute_load(domain=[('id', 'in', self.ids)])
        return True
