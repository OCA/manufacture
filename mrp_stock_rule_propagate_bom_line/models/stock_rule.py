# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    propagate_bom_line = fields.Boolean(
        string="Propagate BOM Line",
        help="Mark this to propagate BOM line information from stock moves generated "
        "by this rule.",
    )
