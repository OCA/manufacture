# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class RepairLine(models.Model):
    _inherit = "repair.line"

    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="repair_line_id",
    )

    def _prepare_stock_move_vals(self):
        return {
            "name": self.repair_id.name,
            "product_id": self.product_id.id,
            "product_uom_qty": self.product_uom_qty,
            "product_uom": self.product_uom.id,
            "partner_id": self.repair_id.address_id.id,  # TODO: check
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "repair_id": self.repair_id.id,
            "repair_line_id": self.id,
            "origin": self.repair_id.name,
            "company_id": self.company_id.id,
        }

    def _prepare_update_stock_move_vals(self):
        return {
            "name": self.repair_id.name,
            "product_id": self.product_id.id,
            "product_uom_qty": self.product_uom_qty,
            "product_uom": self.product_uom.id,
            "partner_id": self.repair_id.address_id.id,  # TODO: check
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "repair_id": self.repair_id.id,
            "repair_line_id": self.id,
            "origin": self.repair_id.name,
            "company_id": self.company_id.id,
        }

    def create_stock_move(self):
        self.ensure_one()
        move = self.env["stock.move"].create(self._prepare_stock_move_vals())
        return move

    def _requires_new_move(self, move):
        return (
            move.location_id != self.location_id
            or move.location_dest_id != self.location_dest_id
            or move.company_id != self.company_id
            or move.product_id != self.product_id
            or False
        )

    def update_stock_move(self):
        self.ensure_one()
        for move in self.stock_move_ids.filtered(
            lambda m: m.state not in ["done", "cancel"]
        ):
            if self._requires_new_move(move):
                move._action_cancel()
                new_move = self.create_stock_move()
                new_move._action_confirm()
                new_move._action_assign()
            else:
                move.write(self._prepare_update_stock_move_vals())
                move._action_assign()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res and res.repair_id.state == "confirmed":
            move = res.create_stock_move()
            move._action_confirm()
            res.move_id = move
        if res and res.repair_id.state == "under_repair":
            move = res.create_stock_move()
            move._action_confirm()
            move._action_assign()
            res.move_id = move
        return res

    def write(self, vals):
        super(RepairLine, self).write(vals)
        for rec in self:
            rec.update_stock_move()
