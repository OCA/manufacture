# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        self._check_negative_quants_after_process()
        return res

    def _check_negative_quants_after_process(self):
        product_ids = self.mapped("move_ids.product_id.id")
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "in", product_ids),
            ]
        )
        quants.check_negative_qty()
