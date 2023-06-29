# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _skip_lot_price_unit_update(self):
        """Skip updating the price unit of the lot for subcontracting receipt moves, as
        price_unit of these records does not reflect the component costs, whereas that
        of the finished product receipt in the subcontracting manufacting order does.
        By skipping the the subcontracting receipt move, price_unit of the lot
        effectively takes the value from the the finished product receipt in the
        subcontracting manufacting order.
        """
        res = super()._skip_lot_price_unit_update()
        if self.move_id.is_subcontract:
            return True
        return res
