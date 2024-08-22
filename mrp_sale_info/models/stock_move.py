# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_orig_created_production_ids(self, already_scanned_ids=None):
        self.ensure_one()
        if self.created_production_id:
            return self.created_production_id
        if not already_scanned_ids:
            # 'already_scanned_ids' is used to avoid infinite loop errors,
            # we only call this method recursively for moves that haven't been handled yet.
            already_scanned_ids = []
        mrp_production_ids = set()
        for move in self.move_orig_ids:
            if move.id in already_scanned_ids:
                return self.env["mrp.production"]
            already_scanned_ids.append(move.id)
            mrp_production_ids.update(
                move._get_orig_created_production_ids(already_scanned_ids).ids
            )
        return self.env["mrp.production"].browse(mrp_production_ids)
