# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def _process(self, cancel_backorder=False):
        """Needed for passing the cancel_backorder context that allows to
        not automatically change the produced quantity in subcontracting.
        """
        return super(
            StockBackorderConfirmation,
            self.with_context(cancel_backorder=cancel_backorder),
        )._process(cancel_backorder=cancel_backorder)
