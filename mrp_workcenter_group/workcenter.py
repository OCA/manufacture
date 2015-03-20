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


class WorkcenterGroup(orm.Model):
    _name = 'workcenter.group'
    _description = 'Workcenter Groups'
    _order = 'sequence ASC, name ASC'

    _columns = {
        'name': fields.char('Name'),
        'sequence': fields.integer('Sequence'),
        'active': fields.boolean('Active'),
        'workcenter_ids': fields.one2many(
            'mrp.workcenter',
            'workcenter_group_id',
            readonly=True,
            string="Workcenters"
            ),
    }

    _defaults = {
        'active': True,
    }


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _columns = {
        'workcenter_group_id': fields.many2one(
            'workcenter.group',
            string='Group'),
    }
