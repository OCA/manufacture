# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.production.workcenter.line"

    sale_id = fields.Many2one(related='production_id.sale_id',
                              string='Sale order', readonly=True, store=True)
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Line',
        related='production_id.sale_line_id')
    partner_id = fields.Many2one(related='sale_id.partner_id', readonly=True,
                                 string='Customer', store=True)
    commitment_date = fields.Datetime(related='sale_id.commitment_date',
                                      string='Commitment Date', store=True,
                                      readonly=True)
