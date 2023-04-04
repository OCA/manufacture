# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_moves_to_assign_with_standard_behavior(self):
        res = super()._get_moves_to_assign_with_standard_behavior()
        # Exclude subcontracting receipt moves from the standard behavior scope.
        return res.filtered(lambda m: not m.is_subcontract)

    # TODO: This should be part of the core.
    def action_show_details(self):
        res = super().action_show_details()
        if "show_owner" in res["context"] and self.is_subcontract:
            res["context"]["show_owner"] = True
        return res
