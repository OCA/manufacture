# -*- coding: utf-8 -*-
#
# Author: Andrea Gallina
# ©  2015 Apulia Software srl
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
