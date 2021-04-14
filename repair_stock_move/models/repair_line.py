# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class RepairLine(models.Model):
    _inherit = "repair.line"

    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="repair_line_id",
    )

    def create_stock_move(self):
        self.ensure_one()
        move = self.env["stock.move"].create(
            {
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
        )
        return move

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

    @api.onchange("product_id")
    def _onchange_location(self):
        if self.state == "draft":
            self.location_id = self.repair_id.location_id

    # TODO: write qty - update stock move.
    # TODO: default repair location in repair lines.
