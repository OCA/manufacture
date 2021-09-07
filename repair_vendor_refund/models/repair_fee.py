# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RepairFee(models.Model):
    _inherit = "repair.fee"

    vendor_refund_move_line_ids = fields.One2many(
        comodel_name="account.move.line", inverse_name="repair_fee_id"
    )
    vendor_to_refund_qty = fields.Float("Vendor Refund Qty")
    vendor_refunded_qty = fields.Float(
        "Vendor Refunded Qty", compute="_compute_vendor_refunded_qty", store=True
    )
    vendor_refund_pending_qty = fields.Float(
        "Vendor Refund Pending Qty", compute="_compute_vendor_refunded_qty", store=True
    )
    parent_state = fields.Selection(
        related="repair_id.state", store=True, readonly=True
    )
    vendor_price_unit = fields.Float("Vendor Unit Price", digits="Product Price")

    @api.depends(
        "vendor_refund_move_line_ids",
        "vendor_refund_move_line_ids.move_id",
        "vendor_refund_move_line_ids.move_id.state",
        "vendor_to_refund_qty",
    )
    def _compute_vendor_refunded_qty(self):
        for rec in self:
            rec.vendor_refunded_qty = sum(
                rec.vendor_refund_move_line_ids.filtered(
                    lambda l: l.move_id.state != "cancel"
                ).mapped("quantity")
            )
            rec.vendor_refund_pending_qty = (
                rec.vendor_to_refund_qty - rec.vendor_refunded_qty
            )

    @api.constrains("vendor_to_refund_qty")
    def _check_vendor_to_refund_qty(self):
        if self.vendor_to_refund_qty > self.product_uom_qty:
            raise ValidationError(
                _(
                    "The Quantity to get Refund from Vendor should less or "
                    "equal to the quantity of the fee."
                )
            )

    @api.onchange("repair_id", "product_id", "product_uom_qty", "vendor_to_refund_qty")
    def onchange_product_id(self):
        super(RepairFee, self).onchange_product_id()
        if not self.product_id:
            return
        taxes = self.product_id.supplier_taxes_id
        fpos = self.env["account.fiscal.position"].get_fiscal_position(
            self.repair_id.vendor_id.id
        )
        taxes_id = fpos.map_tax(taxes, self.product_id, self.repair_id.vendor_id)
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == self.company_id.id
            )
        seller = self.product_id.with_company(self.company_id.id)._select_seller(
            partner_id=self.repair_id.vendor_id,
            quantity=self.vendor_to_refund_qty,
            date=fields.Date.today(),
            uom_id=self.product_id.uom_po_id,
        )
        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price,
                self.product_id.supplier_taxes_id,
                taxes_id,
                self.repair_id.company_id,
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and self.repair_id.currency_id
            and seller.currency_id != self.repair_id.currency_id
        ):
            price_unit = seller.currency_id._convert(
                price_unit,
                self.repair_id.currency_id,
                self.repair_id.company_id,
                fields.Date.today(),
            )
        self.vendor_price_unit = price_unit

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        quantity_to_refund = self.vendor_to_refund_qty - self.vendor_refunded_qty
        taxes = self.product_id.supplier_taxes_id
        fpos = self.env["account.fiscal.position"].get_fiscal_position(
            self.repair_id.vendor_id.id
        )
        taxes_id = fpos.map_tax(taxes, self.product_id, self.repair_id.vendor_id)
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == self.company_id.id
            )
        res = {
            "display_type": False,
            "name": "%s: %s" % (self.repair_id.name, self.name),
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": quantity_to_refund,
            "repair_fee_id": self.id,
            "price_unit": self.vendor_price_unit,
            "tax_ids": [(6, 0, taxes_id.ids)],
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update(
            {
                "move_id": move.id,
                "currency_id": currency and currency.id or False,
                "date_maturity": move.invoice_date_due,
                "partner_id": move.partner_id.id,
            }
        )
        return res
