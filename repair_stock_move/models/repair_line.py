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
            res.move_id = move
            move._set_quantity_done(res.product_uom_qty)
        if res and res.repair_id.state == "under_repair":
            move = res.create_stock_move()
            move._action_confirm()
            move._set_quantity_done(res.product_uom_qty)
            res.move_id = move
        return res

    def unlink(self):
        for rec in self:
            rec.move_id.unlink()
        return super().unlink()
