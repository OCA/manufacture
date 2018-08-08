# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    sale_id = fields.Many2one(related='production_id.sale_id',
                              string='Sale order', readonly=True, store=True)
    partner_id = fields.Many2one(related='sale_id.partner_id', readonly=True,
                                 string='Customer', store=True)
    commitment_date = fields.Datetime(related='sale_id.commitment_date',
                                      string='Commitment Date', store=True,
                                      readonly=True)
