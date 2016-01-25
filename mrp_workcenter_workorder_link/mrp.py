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

from openerp import api, fields, models

# States than we don't want to take account
STATIC_STATES = ['cancel', 'done']

WORKCENTER_ACTION = {
    'res_model': 'mrp.workcenter',
    'type': 'ir.actions.act_window',
    'target': 'current',
}


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    production_line_ids = fields.One2many(
        'mrp.production.workcenter.line',
        'workcenter_id',
        domain=[('state', 'not in', STATIC_STATES)],
        string='Work Orders')
    
    @api.multi
    def _get_workcenter_line_domain(self):
        return [
            ('state', 'not in', STATIC_STATES),
            ('workcenter_id', 'in', self.ids),
            ]

    @api.multi
    def button_workcenter_line(self):
        self.ensure_one()
        domain = self._get_workcenter_line_domain()
        return {
            'view_mode': 'tree,form',
            'name': "'%s' Operations" % self.name,
            'res_model': 'mrp.production.workcenter.line',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'target': 'current',
        }

class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'
    _order = 'sequence ASC, name ASC'

    @api.multi
    def button_workcenter(self):
        self.ensure_one()
        view = self.env.ref('mrp.mrp_workcenter_view')
        action = {
            'view_id': view.id,
            'res_id': self.workcenter_id.id,
            'name': "'%s' Workcenter" % self.name,
            'view_mode': 'form',
        }
        action.update(WORKCENTER_ACTION)
        return action
