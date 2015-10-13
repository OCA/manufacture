# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alex Comba <alex.comba@agilebg.com>
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    _columns = {
        'property_ids': fields.many2many(
            'mrp.property',
            'mrp_production_property_rel',
            'production_id',
            'property_id',
            'Properties'
        ),
    }


class procurement_order(orm.Model):
    _inherit = "procurement.order"

    def make_mo(self, cr, uid, ids, context=None):
        res = super(procurement_order, self).make_mo(
            cr, uid, ids, context=context)
        production_obj = self.pool.get('mrp.production')
        for procurement_id, produce_id in res.iteritems():
            procurement = self.browse(
                cr, uid, procurement_id, context=context)
            production = production_obj.browse(
                cr, uid, produce_id, context=context)
            vals = {
                'property_ids': [
                    (6, 0, [x.id for x in procurement.property_ids])
                ]
            }
            production.write(vals, context=context)
        return res
