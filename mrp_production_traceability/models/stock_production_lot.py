# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

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
