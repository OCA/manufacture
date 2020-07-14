# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductionGroupLineWizard(models.TransientModel):
    _name = 'production.group.line.wizard'
    _description = 'Group mo lines originated from phantom kit'

    mo_id = fields.Many2one(
        'mrp.production', string='Manufacturing Order', required=True)

    @api.model
    def default_get(self, fields):
        res = super(ProductionGroupLineWizard, self).default_get(fields)
        if 'mo_id' in fields and not res.get('mo_id')\
            and self._context.get('active_model') == 'mrp.production'\
                and self._context.get('active_id'):
            res['mo_id'] = self._context['active_id']
        return res

    @api.model
    def group_stock_moves(self, stock_moves):
        stock_move_master = stock_moves[0]
        stock_moves_to_delete = stock_moves - stock_move_master
        qty_total = sum([x.product_uom_qty for x in stock_moves])
        stock_move_master.write({
            'product_uom_qty': qty_total,
            'unit_factor': sum([x.unit_factor for x in stock_moves]),
        })
        stock_moves_to_delete._action_cancel()
        stock_moves_to_delete.unlink()
        stock_move_master._recompute_state()
        stock_move_master._action_assign()
        return True

    @api.multi
    def action_done(self):
        # group move_raw_ids by product if bom origin is phantom
        for wizard in self:
            production = wizard.mo_id
            move_raw_phantom_ids = production.move_raw_ids.filtered(
                lambda x: x.bom_line_id.bom_id.type == 'phantom'
            )
            products = move_raw_phantom_ids.mapped('product_id')
            move_to_group_ids_by_product = {
                product: move_raw_phantom_ids.filtered(
                    lambda y: y.product_id == product and
                    y.product_uom == y.product_id.uom_id
                ) for product in products
            }
            for product in move_to_group_ids_by_product:
                move_to_group_ids = move_to_group_ids_by_product[product]
                if len(move_to_group_ids) > 1:
                    self.group_stock_moves(move_to_group_ids)
        return {}
