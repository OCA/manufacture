# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_id = fields.Many2one('sale.order', compute='_compute_sale_info', string='Sale order',
                              readonly=True)
    partner_id = fields.Many2one('res.partner', compute='_compute_sale_info',
                                 string='Customer')
    commitment_date = fields.Datetime(compute='_compute_sale_info',
                                      string='Commitment Date')

    @api.multi
    def _compute_sale_info(self):
        def get_parent_move(move):
            if move.move_dest_id:
                return get_parent_move(move.move_dest_id)
            return move

        for production in self:
            move = get_parent_move(production.move_finished_ids)
            production.sale_id = move.procurement_id and move.procurement_id.sale_line_id and \
                                 move.procurement_id.sale_line_id.order_id.id or False
            production.partner_id = production.sale_id and production.sale_id.partner_id and production.sale_id.partner_id.id or False
            production.commitment_date = production.sale_id and production.sale_id.commitment_date or ''
