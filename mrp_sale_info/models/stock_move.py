# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_orig_created_production_ids(self):
        self.ensure_one()
        if self.created_production_id:
            return self.created_production_id
        mrp_production_ids = set()
        for move in self.move_orig_ids:
            mrp_production_ids.update(move._get_orig_created_production_ids().ids)
        return self.env["mrp.production"].browse(mrp_production_ids)
