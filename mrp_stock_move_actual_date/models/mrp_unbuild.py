# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpUnbuild(models.Model):
    _name = "mrp.unbuild"
    _inherit = ["mrp.unbuild", "stock.actual.date.mixin"]

    def _get_stock_moves(self):
        self.ensure_one()
        return self.consume_line_ids + self.produce_line_ids

    def action_unbuild(self):
        self.ensure_one()
        self = self.with_context(actual_date_source=self.actual_date)
        return super().action_unbuild()
