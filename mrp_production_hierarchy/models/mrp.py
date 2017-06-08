# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Andrea Gallina
#    Copyright 2015 Apulia Software srl
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

from openerp import models, fields, api


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.one
    @api.depends('name', 'state')
    def _get_parent(self):
        for mrp in self:
            parent = self.search([('name', '=', mrp.origin)], limit=1)
            mrp.parent_id = parent.id

    @api.multi
    def _get_child(self):
        for mrp in self:
            child_ids = self.search([('parent_id', '=', mrp.id)])
            mrp.child_ids |= child_ids

    parent_id = fields.Many2one(
        'mrp.production', compute='_get_parent', store=True)
    child_ids = fields.Many2many(
        comodel_name='mrp.production',
        relation='mrp_production_hierarchy_rel',
        column1='mrp_production_1_id',
        column2='mrp_production_2_id',
        compute='_get_child')

    def _get_master_production(self, recset):
        res = recset
        if recset.parent_id:
            res = self._get_master_production(recset.parent_id)
        return res
