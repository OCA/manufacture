# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    # While https://github.com/odoo/odoo/pull/74268 is not closed.
    def _should_bypass_set_qty_producing(self):
        res = super()._should_bypass_set_qty_producing()
        if self.has_tracking != "none" and float_is_zero(
            self.quantity_done, precision_rounding=self.product_uom.rounding
        ):
            # If some serial/lot has been selected to be consumed we don't change the selection.
            return False
        return res
