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

# States than we don't want to take account
STATIC_STATES = ['cancel', 'done']

WORKCENTER_ACTION = {
    'res_model': 'mrp.workcenter',
    'type': 'ir.actions.act_window',
    'target': 'current',
}


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _columns = {
        'production_line_ids': fields.one2many(
            'mrp.production.workcenter.line',
            'workcenter_id',
            domain=[('state', 'not in', STATIC_STATES)],
            string='Work Orders'),
    }

    def _get_workcenter_line_domain(self, cr, uid, ids, context=None):
        return [
            ('state', 'not in', STATIC_STATES),
            ('workcenter_id', 'in', ids),
            ]

    def button_workcenter_line(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'You can open only an record'
        elm = self.browse(cr, uid, ids[0], context=context)
        domain = elm._get_workcenter_line_domain()
        return {
            'view_mode': 'tree,form',
            'name': "'%s' Operations" % elm.name,
            'res_model': 'mrp.production.workcenter.line',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'target': 'current',
        }


class MrpProductionWorkcenterLine(orm.Model):
    _inherit = 'mrp.production.workcenter.line'
    _order = 'sequence ASC, name ASC'

    def button_workcenter(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'You can open only an record'
        elm = self.browse(cr, uid, ids[0], context=context)
        _, view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'mrp', 'mrp_workcenter_view')
        action = {
            'view_id': view_id,
            'res_id': elm.workcenter_id.id,
            'name': "'%s' Workcenter" % elm.name,
            'view_mode': 'form',
        }
        action.update(WORKCENTER_ACTION)
        return action
