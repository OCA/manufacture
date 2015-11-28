# -*- coding: utf-8 -*-
# (c) 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic Account')
