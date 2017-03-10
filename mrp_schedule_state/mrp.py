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

from openerp import models, api, fields, _
from openerp.exceptions import UserError
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'abstract.selection.rotate']
    _name = 'mrp.production'

    @api.model
    def _set_schedule_states(self):
        return [
            ('waiting', _('Waiting')),
            ('todo', _('To-do')),
            ('scheduled', _('Scheduled')),
        ]

    @api.model
    def _get_schedule_states(self):
        return self._set_schedule_states()

    schedule_state = fields.Selection(
        '_get_schedule_states',
        'Schedule State',
        readonly=True,
        default='waiting',
        help="Schedule State used for ordering production")

    @api.multi
    def _check_planned_state(self):
        productions = self.search([
            ['id', 'in', self.ids],
            ['state', '=', 'confirmed'],
            ['schedule_state', '!=', 'waiting'],
            ])
        if productions:
            production_name = []
            for production in productions:
                production_name.append(production.name)
            raise UserError(
                _('The following production order are not ready and can not '
                  'be scheduled yet : %s') % ', '.join(production_name))
        return True

    _constraints = [
        (_check_planned_state, 'useless', ['schedule_state', 'state']),
    ]

    @api.multi
    def _get_values_from_selection(self, field):
        res = super(MrpProduction, self)._get_values_from_selection(field)
        if field == 'schedule_state':
            # also check model name ?
            res = self._set_schedule_states()
        return res

    @api.multi
    def write(self, vals, update=True):
        if vals.get('schedule_state') == 'scheduled':
            vals['date_planned'] = fields.Datetime.now()
        return super(MrpProduction, self).write(vals, update=update)


class MrpProductionWorkcenterLine(models.Model):
    _inherit = ['mrp.production.workcenter.line', 'abstract.selection.rotate']
    _name = 'mrp.production.workcenter.line'

    @api.model
    def __set_schedule_states(self):
        return self.env['mrp.production']._set_schedule_states()

    schedule_state = fields.Selection(
        '__set_schedule_states',
        related='production_id.schedule_state',
        string='MO Schedule',
        select=True,
        help="'sub state' of MO state 'Ready To Produce' dedicated to "
             "planification, scheduling and ordering",
        store=True,
        readonly=True)
    planned_mo = fields.Datetime(
        related='production_id.date_planned',
        string='Planned MO',
        readonly=True,
        store=True)

    @api.multi
    def _iter_selection(self,direction):
        """ Allows to update the field selection to its next value
            here, we pass through the related field
            to go towards 'schedule_state' in mrp.production
        """
        for elm in self:
            elm.production_id._iter_selection(direction)
        return True
