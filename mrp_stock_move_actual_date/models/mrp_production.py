# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "stock.actual.date.mixin"]

    def _get_actual_date_update_triggers(self):
        return super()._get_actual_date_update_triggers() + [
            "date_finished",
            "move_raw_ids",
            "move_finished_ids",
        ]

    def _get_stock_moves(self):
        self.ensure_one()
        return self.move_raw_ids + self.move_finished_ids
