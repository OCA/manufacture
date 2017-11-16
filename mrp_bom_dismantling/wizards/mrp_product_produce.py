# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MrpByProductLine(models.TransientModel):
    _name = "mrp.product.produced.line"

    produce_id = fields.Many2one('mrp.product.produce', required=True,
                                 string="Produce")
    move_id = fields.Many2one('stock.move', required=True)
    product_id = fields.Many2one('product.product',
                                 related='move_id.product_id')
    lot_id = fields.Many2one('stock.production.lot', string='Lot')

    lot_required = fields.Boolean(compute='_compute_lot_required')

    @api.depends('produce_id.mode', 'product_id.tracking')
    def _compute_lot_required(self):
        for record in self:
            record.lot_required = record.product_id.tracking != 'none' \
                and record.produce_id.mode == 'consume_produce'


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"
    move_lot_ids = fields.One2many(
        'mrp.product.produced.line',
        inverse_name='produce_id',
        string='Products to produce lots'
    )

    @api.onchange("product_id")
    def on_change_product_id(self):
        """ Listen to product_id changes just for filling byproducts_lot_ids.
        """
        if not self.move_lot_ids:
            mrp_prod = self.env["mrp.production"].browse(
                self.env.context['active_id']
            )

            self.move_lot_ids = [
                (0, None, {'move_id': move})
                for move in mrp_prod.move_created_ids
            ]

    @api.multi
    def do_produce(self):
        """ Stock produced products lot_id and call parent do_produce
        """
        mapping_move_lot = {}
        for move_lot in self.move_lot_ids:
            if move_lot.lot_id:
                mapping_move_lot[move_lot.move_id.id] = move_lot.lot_id.id

        super(MrpProductProduce, self.with_context(
            mapping_move_lot=mapping_move_lot
        )).do_produce()
