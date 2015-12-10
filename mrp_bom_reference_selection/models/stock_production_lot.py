# -*- coding: utf-8 -*-
# (c) 2015 Savoir-faire Linux - <http://www.savoirfairelinux.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    bom_id = fields.Many2one(
        comodel_name='mrp.bom', string='Bill of Material')
