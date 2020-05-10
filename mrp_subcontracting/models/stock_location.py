# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def should_bypass_reservation(self):
        if self.env.context.get('mrp_subcontracting_bypass_reservation'):
            return True
        return super().should_bypass_reservation()
