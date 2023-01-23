# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    cost_share = fields.Float(
        "Cost Share (%)",
        digits=(5, 2),
        # decimal = 2 is important for rounding calculations!!
        help="The percentage of the final production cost for this by-product. The"
        " total of all by-products' cost share must be smaller or equal to 100.",
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return super()._prepare_merge_moves_distinct_fields() + ["cost_share"]
