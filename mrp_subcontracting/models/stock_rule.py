# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import models


class StockLocationPath(models.Model):
    _inherit = "stock.location.path"

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super(
            StockLocationPath, self
        )._prepare_move_copy_values(move_to_copy, new_date)
        new_move_vals["is_subcontract"] = False
        return new_move_vals
