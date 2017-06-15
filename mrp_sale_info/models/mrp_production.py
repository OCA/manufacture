# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        comodel_name='sale.order', string='Sale order',
        readonly=True, store=True,
        related='move_prod_id.procurement_id.sale_line_id.order_id')
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Line',
        related='move_prod_id.procurement_id.sale_line_id')
    partner_id = fields.Many2one(related='sale_id.partner_id',
                                 string='Customer', store=True)
    commitment_date = fields.Datetime(related='sale_id.commitment_date',
                                      string='Commitment Date', store=True)
