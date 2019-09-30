# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_mo(self):
        def get_parent_move(move):
            if move.move_dest_id:
                return get_parent_move(move.move_dest_id)
            return move

        res = super(ProcurementOrder, self).make_mo()
        for prod_id in res:
            production = self.env['mrp.production'].browse([res[prod_id]])
            move = get_parent_move(production.move_finished_ids)
            proc = move.procurement_id

            production.sale_id = \
                proc and proc.sale_line_id and \
                proc.sale_line_id.order_id.id or False
            production.partner_id = \
                production.sale_id and production.sale_id.partner_id and \
                production.sale_id.partner_id.id or False
            production.commitment_date = \
                production.sale_id and production.sale_id.commitment_date or ''
        return res
