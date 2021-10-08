# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    to_refurbish = fields.Boolean()
    location_dest_id = fields.Many2one(
        string="Delivery Location", comodel_name="stock.location"
    )
    refurbish_location_dest_id = fields.Many2one(
        string="Refurbished Delivery Location", comodel_name="stock.location"
    )
    refurbish_product_id = fields.Many2one(
        string="Refurbished product", comodel_name="product.product"
    )
    refurbish_lot_id = fields.Many2one(
        string="Refurbished Lot", comodel_name="stock.production.lot"
    )
    refurbish_move_id = fields.Many2one(
        string="Refurbished Inventory Move", comodel_name="stock.move"
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        self.to_refurbish = True if self.product_id.refurbish_product_id else False
        return res

    @api.onchange("to_refurbish", "product_id")
    def _onchange_to_refurbish(self):
        if self.to_refurbish:
            self.refurbish_product_id = self.product_id.refurbish_product_id
            self.refurbish_location_dest_id = self.location_dest_id
            self.location_dest_id = self.product_id.property_stock_refurbish
        else:
            self.location_dest_id = self.refurbish_location_dest_id
            self.refurbish_product_id = False
            self.refurbish_location_dest_id = False

    def _get_refurbish_stock_move_dict(self):
        return {
            "name": self.name,
            "product_id": self.refurbish_product_id.id,
            "product_uom": self.product_uom.id or self.refurbish_product_id.uom_id.id,
            "product_uom_qty": self.product_qty,
            "partner_id": self.address_id and self.address_id.id or False,
            "location_id": self.location_dest_id.id,
            "location_dest_id": self.refurbish_location_dest_id.id,
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.refurbish_product_id.id,
                        "lot_id": self.refurbish_lot_id.id,
                        "product_uom_qty": self.product_qty,
                        "product_uom_id": self.product_uom.id
                        or self.refurbish_product_id.uom_id.id,
                        "qty_done": self.product_qty,
                        "package_id": False,
                        "result_package_id": False,
                        "location_id": self.location_dest_id.id,
                        "location_dest_id": self.refurbish_location_dest_id.id,
                    },
                )
            ],
        }

    def action_repair_done(self):
        res = super(
            RepairOrder,
            self.with_context(
                force_refurbish_location_dest_id=self.location_dest_id.id,
                to_refurbish=self.to_refurbish,
            ),
        ).action_repair_done()
        for repair in self:
            if repair.to_refurbish:
                move = self.env["stock.move"].create(
                    repair._get_refurbish_stock_move_dict()
                )
                move.quantity_done = repair.product_qty
                move._action_done()
                repair.refurbish_move_id = move.id
        return res


class RepairLine(models.Model):
    _inherit = "repair.line"

    @api.onchange("type", "repair_id")
    def onchange_operation_type(self):
        res = super(RepairLine, self).onchange_operation_type()
        context = self.env.context
        if self.type == "add" and "to_refurbish" in context and context["to_refurbish"]:
            self.location_dest_id = context["refurbish_location_dest_id"]
        elif (
            self.type == "add"
            and "to_refurbish" in context
            and not context["to_refurbish"]
        ):
            scrap_location_id = (
                self.env["stock.location"]
                .search(
                    [
                        ("scrap_location", "=", True),
                        ("company_id", "in", [self.repair_id.company_id.id, False]),
                    ],
                    limit=1,
                )
                .id
            )
            self.location_dest_id = scrap_location_id
        return res
