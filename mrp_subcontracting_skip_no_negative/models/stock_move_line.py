# Copyright 2026 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        skip_ids = self.env.context.get("skip_no_negative_move_ids")
        if not skip_ids:
            return super()._action_done()
        skip_ids = set(skip_ids)
        mls_to_skip = self.filtered(lambda ml: ml.move_id.id in skip_ids)
        super(
            StockMoveLine,
            mls_to_skip.with_context(skip_negative_qty_check=True),
        )._action_done()
        super(StockMoveLine, self - mls_to_skip)._action_done()
        return
