# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2011-2014 Akretion
#    Author: Benoît Guillot <benoit.guillot@akretion.com>
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
###############################################################################

from openerp.osv import orm
from datetime import timedelta, datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as ISO_FORMAT
from openerp import SUPERUSER_ID

#Todo Keep-it ?
class ResourceCalendar(orm.Model):
    _inherit = "resource.calendar"

    def _get_date(self, cr, uid, id, start_date, delay, resource=False,
                  context=None):
        """This method gives the first date after a delay from the start date
            considering the working time attached to the company calendar.
            Start_date should be a date not an odoo date
        """
        if not id:
            company_id = self.pool['res.users'].read(
                cr, uid, uid, ['company_id'], context=context)['company_id'][0]
            company = self.pool['res.company'].read(
                cr, uid, company_id, ['calendar_id'], context=context)
            if not company['calendar_id']:
                raise orm.except_orm(
                    _('Error !'),
                    _('You need to define a calendar for the company !'))
            id = company['calendar_id'][0]
        dt_leave = self._get_leaves(cr, uid, id, resource)
        calendar_info = self.browse(cr, SUPERUSER_ID, id, context=context)
        worked_days = [day['dayofweek']
                       for day in calendar_info.attendance_ids]
        if delay < 0:
            delta = -1
        else:
            delta = 1
        while (datetime.strftime(start_date, ISO_FORMAT) in dt_leave or
               str(start_date.weekday()) not in worked_days):
            start_date = start_date + timedelta(days=delta)
        date = start_date
        while delay:
            date = date + timedelta(days=delta)
            if (datetime.strftime(date, ISO_FORMAT) not in dt_leave and
                    str(date.weekday()) in worked_days):
                delay = delay - delta
        return date
