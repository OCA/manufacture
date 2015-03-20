# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2015 Akretion
#    @author David BEAL <david.beal@akretion.com>
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class MrpProduction(orm.Model):
    _inherit = ['mrp.production', 'abstract.selection.rotate']
    _name = 'mrp.production'

    def _set_schedule_states(self, cr, uid, context=None):
        return [
            ('unable', _('Unable')),
            ('todo', _('Todo')),
            ('scheduled', _('Scheduled')),
        ]

    def __set_schedule_states(self, cr, uid, context=None):
        return self._set_schedule_states(cr, uid, context=context)

    _columns = {
        'schedule_state': fields.selection(
            __set_schedule_states,
            'Schedule State',
            readonly=True,
            help="Planification State"),
    }

    _defaults = {
        'schedule_state': 'unable',
    }

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        res = super(MrpProduction, self)._get_values_from_selection(
            cr, uid, ids, field, context=context)
        if field == 'schedule_state':
            # also check model name ?
            # get states and drop 'unable' state
            res = self._set_schedule_states(cr, uid, context=context)[1:]
        return res


class MrpProductionWorkcenterLine(orm.Model):
    _inherit = ['mrp.production.workcenter.line', 'abstract.selection.rotate']
    _name = 'mrp.production.workcenter.line'

    _columns = {
        'schedule_state': fields.related(
            'production_id', 'schedule_state',
            type='char',
            string='MO Schedule',
            help="'sub state' of MO state 'Ready To Produce' dedicated to "
                 "planification, scheduling and ordering"),
    }

    def _iter_selection(self, cr, uid, ids, direction, context=None):
        """ Allows to update the field selection to its next value
            here, we pass through the related field
            to go towards 'schedule_state' in mrp.production
        """
        for elm in self.browse(cr, uid, ids, context=context):
            self.pool['mrp.production']._iter_selection(
                cr, uid, [elm.production_id.id], direction, context=context)
        return True
