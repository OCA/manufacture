# -*- coding: utf-8 -*-
# (c) 2014-2015 Avanzosc
# (c) 2014-2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    estim_std_cost = fields.Float(string='Estimated Standard Cost',
                                  digits=dp.get_precision('Product Price'))
    estim_avg_cost = fields.Float(string='Estimated Average Cost',
                                  digits=dp.get_precision('Product Price'))
