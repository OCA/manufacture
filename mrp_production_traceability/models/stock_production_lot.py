# -*- coding: utf-8 -*-
# Copyright (c)
#    2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
#    2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _, fields


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    track_lot_component_ids = fields.One2many(
        'mrp.track.lot', 'component_lot', readonly=True,
        string="Components tracking"
    )
    track_lot_final_ids = fields.One2many(
        'mrp.track.lot', 'product_lot', readonly=True,
        string="Final Products tracking"
    )
    parent_id = fields.Many2one(
        'stock.production.lot', string="Final production lot", readonly=True)
    children_ids = fields.One2many(
        'stock.production.lot', 'parent_id', 'Components', readonly=True)

    @api.multi
    def total_traceability(self):
        """ It traces the information of lots
        @param self: The object pointer.
        @return: A dictionary of values
        """
        track_lot_obj = self.env["mrp.track.lot"]
        for lot in self:
            track_lot_lst = track_lot_obj.search(
                ['|', ('component_lot', '=', lot.id),
                 ('product_lot', '=', lot.id)])
            moves = set()
            for track_lot in track_lot_lst:
                moves |= {move.id for move in track_lot.st_move}
            if moves:
                return {
                    'domain': "[('id','in',[" + ','.join(map(
                        str, list(moves))) + "])]",
                    'name': _('Full traceability'),
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'context': {'tree_view_ref': 'stock.view_move_tree'},
                    'res_model': 'stock.move',
                    'type': 'ir.actions.act_window',
                    }
        return False
