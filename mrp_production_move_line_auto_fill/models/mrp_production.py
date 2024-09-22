# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    action_op_auto_fill_allowed = fields.Boolean(
        compute="_compute_action_operation_auto_fill_allowed"
    )
    auto_fill_operation = fields.Boolean(
        string="Auto Fill Operations",
        related="picking_type_id.auto_fill_operation",
    )

    @api.depends("state", "move_raw_ids")
    def _compute_action_operation_auto_fill_allowed(self):
        """The auto fill should be enabled when should_consume_qty is set (i.e. the
        state should be either 'progress' or 'to_close').
        """
        for rec in self:
            rec.action_op_auto_fill_allowed = (
                rec.state in ("progress", "to_close") and rec.move_raw_ids
            )

    @api.onchange("qty_producing")
    def _onchange_qty_producing(self):
        # Clear the quantity done of the raw materials whenever the produced qty is
        # changed. User should redo the auto fill if needed.
        if not config["test_enable"]:
            self.move_raw_ids.quantity_done = 0.0

    def _check_action_operation_auto_fill_allowed(self):
        if any(not r.action_op_auto_fill_allowed for r in self):
            raise UserError(
                _(
                    "Filling the operations automatically is not possible. "
                    "Perhaps the productions are not in the right state."
                )
            )

    def action_operation_auto_fill(self):
        self._check_action_operation_auto_fill_allowed()
        operations_to_auto_fill = self.mapped("move_raw_ids").filtered(
            lambda move: (
                move.product_id
                and not move.quantity_done
                and (
                    not move.product_id.tracking != "none"
                    or not move.picking_id.picking_type_id.avoid_lot_assignment
                )
            )
        )
        for move in operations_to_auto_fill:
            move.quantity_done = min(
                move.should_consume_qty, move.reserved_availability
            )
