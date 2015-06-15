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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class MrpProduction(orm.Model):
    _inherit = ['mrp.production', 'abstract.selection.rotate']
    _name = 'mrp.production'

    def _set_schedule_states(self, cr, uid, context=None):
        return [
            ('waiting', _('Waiting')),
            ('todo', _('To-do')),
            ('scheduled', _('Scheduled')),
        ]

    def __set_schedule_states(self, cr, uid, context=None):
        return self._set_schedule_states(cr, uid, context=context)

    _columns = {
        'schedule_state': fields.selection(
            __set_schedule_states,
            'Schedule State',
            readonly=True,
            help="Schedule State used for ordering production"),
    }

    _defaults = {
        'schedule_state': 'waiting',
    }

    def _check_planned_state(self, cr, uid, ids, context=None):
        production_ids = self.search(cr, uid, [
            ['id', 'in', ids],
            ['state', '=', 'confirmed'],
            ['schedule_state', '!=', 'waiting'],
            ], context=context)
        if production_ids:
            production_name = []
            for production in self.browse(cr, uid, production_ids,
                                          context=context):
                production_name.append(production.name)
            raise orm.except_orm(
                _('Error'),
                _('The following production order are not ready and can not '
                  'be scheduled yet : %s') % ', '.join(production_name))
        return True

    _constraints = [
        (_check_planned_state, 'useless', ['schedule_state', 'state']),
    ]

    def _get_values_from_selection(self, cr, uid, ids, field, context=None):
        res = super(MrpProduction, self)._get_values_from_selection(
            cr, uid, ids, field, context=context)
        if field == 'schedule_state':
            # also check model name ?
            res = self._set_schedule_states(cr, uid, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None, update=True):
        if context is None:
            context = {}
        if vals.get('schedule_state') == 'scheduled':
            vals['date_planned'] =\
                datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        return super(MrpProduction, self)\
            .write(cr, uid, ids, vals, context=context, update=update)


class MrpProductionWorkcenterLine(orm.Model):
    _inherit = ['mrp.production.workcenter.line', 'abstract.selection.rotate']
    _name = 'mrp.production.workcenter.line'

    def _get_operation_from_production(self, cr, uid, ids, context=None):
        return self.pool['mrp.production.workcenter.line'].search(cr, uid, [
            ['production_id', '=', ids],
            ], context=context)

    _columns = {
        'schedule_state': fields.related(
            'production_id', 'schedule_state',
            type='char',
            string='MO Schedule',
            help="'sub state' of MO state 'Ready To Produce' dedicated to "
                 "planification, scheduling and ordering"),
        'planned_mo': fields.related(
            'production_id',
            'date_planned',
            type='date',
            string='Planned MO',
            readonly=True,
            store={
                'mrp.production': [
                    _get_operation_from_production,
                    ['date_planned'],
                    10,
                ],
            })
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
