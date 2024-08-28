# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_picking_ids",
        copy=False,
        string="Transfers",
    )
    picking_count = fields.Integer(
        string="Transfers", copy=False, compute="_compute_picking_ids"
    )

    def action_view_pickings(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        action["domain"] = [("id", "in", self.picking_ids.ids)]
        return action

    def _compute_picking_ids(self):
        for order in self:
            moves = self.env["stock.move"].search(
                [
                    "|",
                    ("repair_id", "=", order.id),
                    ("repair_line_id", "in", order.operations.ids),
                ]
            )
            order.picking_ids = moves.mapped("picking_id")
            order.picking_count = len(moves.mapped("picking_id"))
