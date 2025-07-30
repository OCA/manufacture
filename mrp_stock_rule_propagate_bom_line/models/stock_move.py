# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    bom_id = fields.Many2one("mrp.bom", related="bom_line_id.bom_id")

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        # If the ``rule_id`` is set and ``propagate_bom_line`` is unchecked,
        # we remove the ``bom_line_id`` from the procurement values
        # to allow the grouping of moves with different BOM lines.
        if self.rule_id and not self.rule_id.propagate_bom_line:
            res.pop("bom_line_id", None)
        return res
