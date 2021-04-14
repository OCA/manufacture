# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class RepairOrder(models.Model):
    _inherit = "repair.order"

    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="repair_id",
    )
    show_check_availability = fields.Boolean(
        compute="_compute_show_check_availability",
        help="Technical field used to compute whether the button "
        "'Check Availability' should be displayed.",
    )
    ignore_availability = fields.Boolean()
    # Make "Parts" editable in more states.
    operations = fields.One2many(
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "ready": [("readonly", False)],
        },
    )
    fees_lines = fields.One2many(
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "ready": [("readonly", False)],
        },
    )

    @api.depends("state")
    def _compute_show_check_availability(self):
        for rec in self:
            rec.show_check_availability = (
                any(
                    move.state in ("waiting", "confirmed", "partially_available")
                    and float_compare(
                        move.product_uom_qty,
                        0,
                        precision_rounding=move.product_uom.rounding,
                    )
                    for move in rec.stock_move_ids
                )
                and not rec.ignore_availability
            )

    def _create_repair_stock_move(self):
        self.ensure_one()
        return self.env["stock.move"].create(
            {
                "name": self.name,
                "product_id": self.product_id.id,
                "product_uom": self.product_uom.id or self.product_id.uom_id.id,
                "product_uom_qty": self.product_qty,
                "partner_id": self.address_id.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_id.id,
                "repair_id": self.id,
                "origin": self.name,
                "company_id": self.company_id.id,
            }
        )

    def action_repair_confirm(self):
        res = super().action_repair_confirm()
        for repair in self:
            moves = self.env["stock.move"]
            for operation in repair.operations:
                move = operation.create_stock_move()
                moves |= move
                operation.write({"move_id": move.id})
            move = repair._create_repair_stock_move()
            repair.move_id = move
        self.mapped("stock_move_ids")._action_confirm()
        return res

    def action_assign(self):
        self.filtered(lambda r: r.state == "draft").action_repair_start()
        moves = self.mapped("stock_move_ids")
        moves = moves.filtered(
            lambda move: move.state not in ("draft", "cancel", "done")
        )
        if not moves:
            raise UserError(_("Nothing to check the availability for."))
        moves._action_assign()
        return True

    def action_repair_start(self):
        res = super().action_repair_start()
        self.mapped("stock_move_ids")._action_assign()
        return res

    def action_force_availability(self):
        self.write({"ignore_availability": True})

    def _force_qty_done_in_repair_lines(self):
        for operation in self.mapped("operations"):
            for move in operation.stock_move_ids:
                if move.state not in ["confirmed", "waiting", "partially_available"]:
                    continue
                product_qty = move.product_uom._compute_quantity(
                    operation.product_uom_qty,
                    move.product_id.uom_id,
                    rounding_method="HALF-UP",
                )
                available_quantity = self.env["stock.quant"]._get_available_quantity(
                    move.product_id,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._update_reserved_quantity(
                    product_qty - move.reserved_availability,
                    available_quantity,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._set_quantity_done(operation.product_uom_qty)
                if operation.lot_id:
                    move.move_line_ids.lot_id = operation.lot_id

    def action_open_stock_moves(self):
        self.ensure_one()
        domain = [("id", "in", self.mapped("stock_move_ids").ids)]
        action = {
            "name": _("Stock Moves"),
            "view_type": "tree",
            "view_mode": "list,form",
            "res_model": "stock.move",
            "type": "ir.actions.act_window",
            "context": self.env.context,
            "domain": domain,
        }
        return action

    def action_repair_cancel(self):
        self.mapped("stock_move_ids")._action_cancel()
        return super().action_repair_cancel()

    def action_repair_end(self):
        if any(r.show_check_availability for r in self):
            raise UserError(_("Some related stock moves are not available."))
        # I can not everything has been reserved.
        self._force_qty_done_in_repair_lines()
        for repair in self:
            operation_moves = repair.mapped("operations.move_id")
            if operation_moves:
                consumed_lines = operation_moves.mapped("move_line_ids")
                produced_lines = repair.move_id.move_line_ids
                operation_moves |= repair.move_id
                produced_lines.write({"consume_line_ids": [(6, 0, consumed_lines.ids)]})

        self.move_id._set_quantity_done(self.move_id.product_uom_qty)
        self.move_id._action_done()
        for move in self.mapped("operations.move_id"):
            move._set_quantity_done(move.product_uom_qty)
            move._action_done()
        return super().action_repair_end()

    def action_repair_done(self):
        self.ensure_one()
        if self.stock_move_ids:
            # With this module this should always be the case, so this is
            # effectively overriding the method.
            return {self.id: self.move_id.id}
        return super().action_repair_done()
