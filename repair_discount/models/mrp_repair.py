# Copyright 2015 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairFee(models.Model):
    _inherit = "repair.fee"

    discount = fields.Float(string="Discount (%)")

    @api.depends("price_unit", "repair_id", "product_uom_qty", "product_id", "discount")
    def _compute_price_subtotal(self):
        for fee in self:
            taxes = self.env["account.tax"].compute_all(
                fee.price_unit,
                fee.repair_id.pricelist_id.currency_id,
                fee.product_uom_qty,
                fee.product_id,
                fee.repair_id.partner_id,
            )
            fee.price_subtotal = taxes["total_excluded"] * (
                1 - (fee.discount or 0.0) / 100.0
            )

    @api.depends(
        "price_unit", "repair_id", "product_uom_qty", "product_id", "tax_id", "discount"
    )
    def _compute_price_total(self):
        for fee in self:
            taxes = fee.tax_id.compute_all(
                fee.price_unit,
                fee.repair_id.pricelist_id.currency_id,
                fee.product_uom_qty,
                fee.product_id,
                fee.repair_id.partner_id,
            )
            fee.price_total = taxes["total_included"] * (
                1 - (fee.discount or 0.0) / 100.0
            )


class RepairLine(models.Model):
    _inherit = "repair.line"

    discount = fields.Float(string="Discount (%)")

    @api.depends(
        "price_unit",
        "repair_id",
        "product_uom_qty",
        "product_id",
        "repair_id.invoice_method",
        "discount",
    )
    def _compute_price_subtotal(self):
        for line in self:
            taxes = self.env["account.tax"].compute_all(
                line.price_unit,
                line.repair_id.pricelist_id.currency_id,
                line.product_uom_qty,
                line.product_id,
                line.repair_id.partner_id,
            )
            line.price_subtotal = taxes["total_excluded"] * (
                1 - (line.discount or 0.0) / 100.0
            )

    @api.depends(
        "price_unit",
        "repair_id",
        "product_uom_qty",
        "product_id",
        "tax_id",
        "repair_id.invoice_method",
        "discount",
    )
    def _compute_price_total(self):
        for line in self:
            taxes = line.tax_id.compute_all(
                line.price_unit,
                line.repair_id.pricelist_id.currency_id,
                line.product_uom_qty,
                line.product_id,
                line.repair_id.partner_id,
            )
            line.price_total = taxes["total_included"] * (
                1 - (line.discount or 0.0) / 100.0
            )


class RepairOrder(models.Model):
    _inherit = "repair.order"

    def _create_invoices(self, group=False):

        res = super(RepairOrder, self)._create_invoices(group)
        for repair in self.filtered(lambda _repair: _repair.invoice_method != "none"):
            operations = repair.operations
            fees_lines = repair.fees_lines
            for op in operations.filtered(
                lambda item: item.discount and item.invoice_line_id
            ):
                op.invoice_line_id.with_context(check_move_validity=False).update(
                    {"discount": op.discount}
                )
            for fee_lines in fees_lines.filtered(
                lambda item: item.discount and item.invoice_line_id
            ):
                fee_lines.invoice_line_id.with_context(
                    check_move_validity=False
                ).update({"discount": fee_lines.discount})
        self.invoice_id.with_context(
            check_move_validity=False
        )._recompute_dynamic_lines(
            recompute_all_taxes=True, recompute_tax_base_amount=True
        )
        return res

    def _calculate_line_base_price(self, line):
        return line.price_unit * (1 - (line.discount or 0.0) / 100.0)

    @api.depends(
        "operations", "fees_lines", "operations.invoiced", "fees_lines.invoiced"
    )
    def _amount_tax(self):
        for repair in self:
            taxed_amount = 0.0
            currency = repair.pricelist_id.currency_id

            for line in repair.operations:
                tax_calculate = line.tax_id.compute_all(
                    self._calculate_line_base_price(line),
                    self.pricelist_id.currency_id,
                    line.product_uom_qty,
                    line.product_id,
                    repair.partner_id,
                )

                for c in tax_calculate["taxes"]:
                    taxed_amount += c["amount"]

            for line in repair.fees_lines:
                tax_calculate = line.tax_id.compute_all(
                    self._calculate_line_base_price(line),
                    self.pricelist_id.currency_id,
                    line.product_uom_qty,
                    line.product_id,
                    repair.partner_id,
                )
                for c in tax_calculate["taxes"]:
                    taxed_amount += c["amount"]

            repair.amount_tax = currency.round(taxed_amount)
