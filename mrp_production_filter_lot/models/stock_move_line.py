# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_use_filter_lots = fields.Boolean(
        compute="_compute_picking_type_use_filter_lots",
        # Disable related field that has been set
        # in the dependency `stock_picking_filter_lot`.
        related=None,
    )

    @api.depends(
        "picking_id.picking_type_id.use_filter_lots",
        "production_id.picking_type_id.use_filter_lots",
    )
    def _compute_picking_type_use_filter_lots(self):
        for line in self:
            picking_type = (
                line.picking_id.picking_type_id or line.production_id.picking_type_id
            )
            line.picking_type_use_filter_lots = picking_type.use_filter_lots
