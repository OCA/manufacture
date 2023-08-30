# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class MrpWorkOrderNewLine(models.TransientModel):
    _name = "mrp.workorder.new.line"
    _description = "MRP Work Order New Line"

    product_id = fields.Many2one("product.product", required=True, readonly=True)

    workorder_id = fields.Many2one(
        "mrp.workorder", "Work Order", required=True, check_company=True
    )

    workorder_line_id = fields.Many2one(
        "mrp.workorder.line", "Work Order Line", required=True, check_company=True
    )

    product_qty = fields.Float(
        "Quantity", default=1.0, required=True, digits="Product Unit of Measure"
    )

    original_line_qty = fields.Float(
        "Original Quantity",
        readonly=True,
        required=True,
        digits="Product Unit of Measure",
    )

    lot_id = fields.Many2one(
        "stock.production.lot",
        string="Lot/Serial Number",
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",
    )

    company_id = fields.Many2one("res.company", string="Company")

    def action_validate(self):
        old_available_quantity = self.env["stock.quant"]._get_available_quantity(
            self.workorder_line_id.move_id.product_id,
            self.workorder_line_id.move_id.location_id,
            lot_id=self.workorder_line_id.lot_id,
        )
        new_available_quantity = self.env["stock.quant"]._get_available_quantity(
            self.workorder_line_id.move_id.product_id,
            self.workorder_line_id.move_id.location_id,
            lot_id=self.lot_id,
        )
        if (
            float_compare(
                new_available_quantity,
                self.product_qty,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            < 0
        ):
            self.not_enought_qty_to_reserve(new_available_quantity)
        self.workorder_line_id.write(
            {
                "qty_done": self.workorder_line_id.qty_done - self.product_qty,
                "qty_to_consume": self.workorder_line_id.qty_to_consume
                - self.product_qty,
                "qty_reserved": self.workorder_line_id.qty_reserved - self.product_qty,
            }
        )
        self.workorder_line_id.move_id._update_reserved_quantity(
            -self.product_qty,
            old_available_quantity,
            self.workorder_line_id.move_id.location_id,
            lot_id=self.workorder_line_id.lot_id,
        )
        self.workorder_line_id.move_id._update_reserved_quantity(
            self.product_qty,
            new_available_quantity,
            self.workorder_line_id.move_id.location_id,
            lot_id=self.lot_id,
        )
        line_values = self.workorder_id._generate_lines_values(
            self.workorder_line_id.move_id, self.product_qty
        )
        for value in line_values:
            value["lot_id"] = self.lot_id.id
        self.env["mrp.workorder.line"].create(line_values)

    def not_enought_qty_to_reserve(self, new_available_quantity):
        raise ValidationError(
            _("The quantity must be lower or equal than the available quantity: %s.")
            % (new_available_quantity)
        )

    @api.constrains("product_qty")
    def _check_product_qty(self):
        if (
            float_compare(
                self.product_qty,
                self.original_line_qty,
                precision_rounding=self.product_id.uom_id.rounding,
            )
            >= 0
        ):
            raise ValidationError(
                _("The quantity must be lower than the original line quantity: %s.")
                % (self.original_line_qty)
            )
