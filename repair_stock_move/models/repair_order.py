# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class RepairOrder(models.Model):
    _inherit = "repair.order"

    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="repair_id",
    )
    operations = fields.One2many(
        comodel_name="repair.line",
        inverse_name="repair_id",
        string="Parts",
        copy=True,
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "ready": [("readonly", False)],
        },
    )

    product_qty = fields.Float(
        "Product Quantity",
        default=1.0,
        digits="Product Unit of Measure",
        readonly=True,
        required=True,
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "ready": [("readonly", False)],
        },
    )

    fees_lines = fields.One2many(
        comodel_name="repair.fee",
        inverse_name="repair_id",
        string="Operations",
        copy=True,
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "ready": [("readonly", False)],
        },
    )

    def action_validate(self):
        res = super().action_validate()
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        res = {}
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        Move = self.env["stock.move"]
        for repair in self:
            # Try to create move with the appropriate owner
            owner_id = False
            available_qty_owner = self.env["stock.quant"]._get_available_quantity(
                repair.product_id,
                repair.location_id,
                repair.lot_id,
                strict=True,
            )
            if available_qty_owner <= 0.0:
                raise ValidationError(
                    _("There is no stock of product: ") + repair.product_id.display_name
                )
            if (
                float_compare(
                    available_qty_owner, repair.product_qty, precision_digits=precision
                )
                >= 0
            ):
                owner_id = repair.partner_id.id

            moves = self.env["stock.move"]
            for operation in repair.operations:
                move = operation.create_stock_move()
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
                    product_qty,
                    available_quantity,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._set_quantity_done(operation.product_uom_qty)

                if operation.lot_id:
                    move.move_line_ids.lot_id = operation.lot_id

                moves |= move
                operation.write({"move_id": move.id, "state": "draft"})
            move = Move.create(
                {
                    "name": repair.name,
                    "product_id": repair.product_id.id,
                    "product_uom": repair.product_uom.id or repair.product_id.uom_id.id,
                    "product_uom_qty": repair.product_qty,
                    "partner_id": repair.address_id.id,
                    "location_id": repair.location_id.id,
                    "location_dest_id": repair.location_id.id,
                    "move_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": repair.product_id.id,
                                "lot_id": repair.lot_id.id,
                                "product_uom_qty": 0,  # bypass reservation here
                                "product_uom_id": repair.product_uom.id
                                or repair.product_id.uom_id.id,
                                "qty_done": repair.product_qty,
                                "package_id": False,
                                "result_package_id": False,
                                "owner_id": owner_id,
                                "location_id": repair.location_id.id,  # TODO:ownerstuff
                                "company_id": repair.company_id.id,
                                "location_dest_id": repair.location_id.id,
                            },
                        )
                    ],
                    "repair_id": repair.id,
                    "origin": repair.name,
                    "company_id": repair.company_id.id,
                }
            )
            consumed_lines = moves.mapped("move_line_ids")
            produced_lines = move.move_line_ids
            moves |= move
            produced_lines.write({"consume_line_ids": [(6, 0, consumed_lines.ids)]})
            res[repair.id] = move.id
            repair.move_id = move
        return res

    def action_repair_start(self):
        super().action_repair_start()
        (self.move_id | self.operations.mapped("move_id"))._action_confirm()

    def action_open_stock_moves(self):
        self.ensure_one()
        stock_move_ids = self.move_id.ids + self.operations.move_id.ids
        domain = [("id", "in", stock_move_ids)]
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
        if self.move_id.state != "draft" or self.operations:
            raise ValidationError(
                _("Unable to cancel repair order due to already generated stock moves.")
            )
        else:
            super().action_repair_cancel()
