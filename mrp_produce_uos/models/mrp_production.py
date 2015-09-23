# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_produce(self, production_id, production_qty,
                       production_mode, wiz=False):
        res = super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz)

        mrp_production = self.browse(production_id)

        for move in mrp_production.move_created_ids2:
            product_uom_qty = move.product_uom_qty
            p_qty = mrp_production.product_qty
            p_uos_qty = mrp_production.product_uos_qty
            product_uos_qty = p_uos_qty * (product_uom_qty / p_qty)
            # I used sql to avoid
            # https://github.com/odoo/odoo/blob/8.0/addons/stock/stock.py#L1980
            self.env.cr.execute(
                'UPDATE stock_move SET product_uos_qty = %s '
                'WHERE id = %s',
                (product_uos_qty, move.id)
            )

        return res
