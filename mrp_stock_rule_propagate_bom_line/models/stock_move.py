# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    bom_id = fields.Many2one("mrp.bom", related="bom_line_id.bom_id")

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        if self.bom_line_id and self.rule_id.propagate_bom_line:
            res["bom_line_id"] = self.bom_line_id.id
        return res
