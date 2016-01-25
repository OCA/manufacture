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

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
    _order = 'parent_left'
    _parent_store = True
    
    parent_id = fields.Many2one('mrp.workcenter', string='Parent')            
    child_ids = fields.One2many(
        'mrp.workcenter',
        'parent_id',
        string='Children')
    parent_level_1_id = fields.Many2one(
        'mrp.workcenter',
        compute='_compute_parent_level',
        string='Parent Level 1',
        store=True)
    parent_level_2_id = fields.Many2one(
        'mrp.workcenter',
        compute='_compute_parent_level',
        string='Parent Level 2',
        store=True)
    parent_level_3_id = fields.Many2one(
        'mrp.workcenter',
        compute='_compute_parent_level',
        string='Parent Level 3',
        store=True)
    parent_left=fields.Integer(select=1)
    parent_right=fields.Integer(select=1)
    
    @api.multi
    def _get_parent_ids(self):
        self.ensure_one()
        if self.parent_id:
            ids = self.parent_id._get_parent_ids()
            ids.append(self.parent_id.id)
        else:
            ids = []
        return ids
       
    @api.multi
    @api.depends('parent_id.parent_id.parent_id', 'child_ids')
    def _compute_parent_level(self):
        def get_next_level(parent_ids, workcenter):
            return parent_ids and parent_ids.pop(0) or (
                workcenter.child_ids and workcenter.id
                or workcenter.parent_id.id)

        for workcenter in self:
            parent_ids = workcenter._get_parent_ids()
            workcenter.parent_level_1_id = get_next_level(parent_ids, workcenter)
            workcenter.parent_level_2_id = get_next_level(parent_ids, workcenter)
            workcenter.parent_level_3_id = get_next_level(parent_ids, workcenter)

    
