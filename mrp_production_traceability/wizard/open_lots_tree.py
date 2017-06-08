# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class OpenLotsTree(models.TransientModel):
    _name = 'stock.production.lot.open.tree'
    lot_id = fields.Many2one(
        'stock.production.lot', required=True, string="Production lot")

    @api.multi
    def open_lots_tree(self):
        self.ensure_one()
        data_model = self.env['ir.model.data']
        act_model = self.env['ir.actions.act_window']
        id = data_model.get_object_reference(
            'mrp_production_traceability', 'action_lot_traceability_tree')[1]
        result = act_model.browse(id).read()[0]
        result['domain'] = [('id', '=', self.lot_id.id)]
        return result
