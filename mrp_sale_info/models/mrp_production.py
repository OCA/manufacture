# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale order',
        readonly=True)
    partner_id = fields.Many2one(
        'res.partner',
        readonly=True,
        string='Customer')
    commitment_date = fields.Datetime(string='Commitment Date')
