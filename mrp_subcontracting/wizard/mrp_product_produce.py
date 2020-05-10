# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import fields, models
from odoo.tools.float_utils import float_is_zero


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    subcontract_move_id = fields.Many2one(
        'stock.move', 'stock move from the subcontract picking')

    def _get_todo(self, production):
        """This method will return remaining todo quantity of production."""
        main_product_moves = production.move_finished_ids.filtered(
            lambda x: x.product_id == production.product_id)
        todo_quantity = production.product_qty - sum(
            main_product_moves.mapped('quantity_done'))
        return todo_quantity if (todo_quantity > 0) else 0

    def do_produce(self):
        """ After producing, set the move line on the subcontract picking. """
        res = super().do_produce()
        if self.subcontract_move_id:
            self.env['stock.move.line'].create({
                'move_id': self.subcontract_move_id.id,
                'picking_id': self.subcontract_move_id.picking_id.id,
                'product_id': self.product_id.id,
                'location_id': self.subcontract_move_id.location_id.id,
                'location_dest_id': (
                    self.subcontract_move_id.location_dest_id.id),
                'product_uom_qty': 0,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': self.product_qty,
                'lot_id': self.lot_id.id,
            })
            if not self._get_todo(self.production_id):
                ml_reserved = self.subcontract_move_id.move_line_ids.filtered(
                    lambda ml: (
                        float_is_zero(
                            ml.qty_done,
                            precision_rounding=ml.product_uom_id.rounding
                        ) and not float_is_zero(
                            ml.product_uom_qty,
                            precision_rounding=ml.product_uom_id.rounding
                        )
                    )
                )
                ml_reserved.unlink()
                for ml in self.subcontract_move_id.move_line_ids:
                    ml.product_uom_qty = ml.qty_done
                self.subcontract_move_id._recompute_state()
        return res
