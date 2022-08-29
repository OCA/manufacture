# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    subcontracting_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        compute="_compute_subcontracting_purchase_order_id",
        store=True,
        string="Subcontracting order",
    )

    @api.depends("move_lines", "move_lines.rule_id", "move_lines.move_dest_ids")
    def _compute_subcontracting_purchase_order_id(self):
        for item in self:
            move_dests = item.move_lines.filtered(
                lambda x: x.rule_id and x.move_dest_ids
            )
            order_id = False
            if move_dests:
                productions = move_dests.mapped(
                    "move_dest_ids.raw_material_production_id"
                )
                group = productions.picking_ids.group_id
                moves = group.stock_move_ids.move_dest_ids.filtered(
                    lambda x: x.is_subcontract and x.purchase_line_id
                )
                order_id = fields.first(moves.mapped("purchase_line_id.order_id"))
            item.subcontracting_purchase_order_id = order_id
