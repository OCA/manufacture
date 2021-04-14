# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    repair_line_id = fields.Many2one(
        comodel_name="repair.line",
        string="Repair Line",
        ondelete="cascade",
    )
